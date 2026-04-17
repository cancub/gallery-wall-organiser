from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from gallery_wall_organiser.geometry import compute_cost, is_within_bounds, overlaps_obstacle, placements_overlap
from gallery_wall_organiser.models import Layout, Placement

if TYPE_CHECKING:
    from gallery_wall_organiser.models import Obstacle, Photo, Wall


def _find_free_position(
    photo: Photo,
    wall: Wall,
    obstacles: list[Obstacle],
    existing: list[Placement],
) -> Placement | None:
    """Brute-force search for a valid position on a 10-unit grid."""
    for y in range(0, int(wall.height), 10):
        for x in range(0, int(wall.width), 10):
            candidate = Placement(photo=photo, x=float(x), y=float(y))
            if (
                is_within_bounds(candidate, wall)
                and not any(overlaps_obstacle(candidate, obs) for obs in obstacles)
                and not any(placements_overlap(candidate, p) for p in existing)
            ):
                return candidate
    return None


def initialize_grid(
    wall: Wall,
    photos: list[Photo],
    obstacles: list[Obstacle],
    eye_level: float,
) -> Layout:
    """Place photos in a grid layout avoiding obstacles, within wall bounds."""
    n = len(photos)
    if n == 0:
        return Layout(wall=wall, placements=[], obstacles=obstacles, d=0, eye_level=eye_level)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    max_w = max(p.width for p in photos)
    max_h = max(p.height for p in photos)
    gap_x = (wall.width - cols * max_w) / (cols + 1)
    gap_y = (wall.height - rows * max_h) / (rows + 1)
    placements: list[Placement] = []
    for i, photo in enumerate(photos):
        row, col = divmod(i, cols)
        cx = gap_x * (col + 1) + max_w * col + (max_w - photo.width) / 2
        cy = gap_y * (row + 1) + max_h * row + (max_h - photo.height) / 2
        p = Placement(photo=photo, x=cx, y=cy)
        if any(overlaps_obstacle(p, obs) for obs in obstacles):
            fallback = _find_free_position(photo, wall, obstacles, placements)
            if fallback is not None:
                p = fallback
        placements.append(p)
    return Layout(wall=wall, placements=placements, obstacles=obstacles, d=0, eye_level=eye_level)


def _with_placements(layout: Layout, placements: list[Placement]) -> Layout:
    return Layout(
        wall=layout.wall,
        placements=placements,
        obstacles=layout.obstacles,
        d=layout.d,
        eye_level=layout.eye_level,
    )


def perturb_position(layout: Layout, index: int, max_delta: float) -> Layout:
    """Return a new Layout with placement at index shifted by a random delta."""
    new_placements = list(layout.placements)
    p = new_placements[index]
    dx = random.uniform(-max_delta, max_delta)
    dy = random.uniform(-max_delta, max_delta)
    new_placements[index] = Placement(photo=p.photo, x=p.x + dx, y=p.y + dy)
    return _with_placements(layout, new_placements)


def swap_placements(layout: Layout, i: int, j: int) -> Layout:
    """Return a new Layout with placements at indices i and j swapped."""
    new_placements = list(layout.placements)
    new_placements[i], new_placements[j] = new_placements[j], new_placements[i]
    return _with_placements(layout, new_placements)


def accept(delta_cost: float, temperature: float) -> bool:
    """Metropolis acceptance criterion for simulated annealing.
    
    Returns True if the move should be accepted, False otherwise.
    - Improvement (delta_cost <= 0) is always accepted.
    - At zero temperature, only improvement or no-change is accepted.
    - Otherwise, accept with probability exp(-delta_cost / temperature).
    """
    if delta_cost <= 0:
        return True
    if temperature == 0:
        return False
    return random.random() < math.exp(-delta_cost / temperature)


def _generate_candidate(layout: Layout, max_delta: float) -> Layout:
    n = len(layout.placements)
    if random.random() < 0.5:
        idx = random.randint(0, n - 1)
        return perturb_position(layout, idx, max_delta)
    a = random.randint(0, n - 1)
    b = random.randint(0, n - 1)
    return swap_placements(layout, a, b)


def optimize(
    wall: Wall,
    photos: list[Photo],
    obstacles: list[Obstacle],
    eye_level: float,
    max_iterations: int,
    seed: int,
) -> Layout:
    """Simulated annealing optimizer for photo placement."""
    random.seed(seed)
    current = initialize_grid(wall, photos, obstacles, eye_level)
    current_cost = compute_cost(current)
    best = current
    best_cost = current_cost
    if not photos:
        return current
    t0 = 1000.0
    scale = max(wall.width, wall.height) * 0.1
    for i in range(max_iterations):
        progress = 1.0 - i / max_iterations
        candidate = _generate_candidate(current, scale * progress)
        candidate_cost = compute_cost(candidate)
        if accept(candidate_cost - current_cost, t0 * progress):
            current = candidate
            current_cost = candidate_cost
            if current_cost < best_cost:
                best = current
                best_cost = current_cost
    return best
