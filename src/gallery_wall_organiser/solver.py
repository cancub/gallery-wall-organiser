from __future__ import annotations

import math
from typing import TYPE_CHECKING

from gallery_wall_organiser.geometry import is_within_bounds, overlaps_obstacle, placements_overlap
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
