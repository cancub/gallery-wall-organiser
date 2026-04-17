from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from scipy.spatial import Delaunay, QhullError

if TYPE_CHECKING:
    from gallery_wall_organiser.models import Obstacle, Placement, Wall

Rectangle = tuple[float, float, float, float]  # (x, y, width, height)


def _placement_rect(p: Placement) -> Rectangle:
    return (p.x, p.y, p.photo.width, p.photo.height)


def _obstacle_rect(o: Obstacle) -> Rectangle:
    return (o.x, o.y, o.width, o.height)


def rectangles_overlap(r1: Rectangle, r2: Rectangle) -> bool:
    """Return True if two rectangles overlap (touching edges do not count)."""
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1


def is_within_bounds(placement: Placement, wall: Wall) -> bool:
    """Return True if the placement lies entirely within the wall boundaries."""
    return (
        placement.left >= 0
        and placement.top >= 0
        and placement.right <= wall.width
        and placement.bottom <= wall.height
    )


def overlaps_obstacle(placement: Placement, obstacle: Obstacle) -> bool:
    """Return True if a placement overlaps an obstacle (touching edges do not count)."""
    return rectangles_overlap(_placement_rect(placement), _obstacle_rect(obstacle))


def placements_overlap(p1: Placement, p2: Placement) -> bool:
    """Return True if two placements overlap (touching edges do not count)."""
    return rectangles_overlap(_placement_rect(p1), _placement_rect(p2))


def edge_distance(p1: Placement, p2: Placement) -> float:
    """Return the minimum edge-to-edge distance between two placements."""
    h_gap = max(0, max(p1.left, p2.left) - min(p1.right, p2.right))
    v_gap = max(0, max(p1.top, p2.top) - min(p1.bottom, p2.bottom))
    return math.hypot(h_gap, v_gap)


def build_adjacency(placements: list[Placement]) -> list[tuple[int, int]]:
    """Return unique edges from Delaunay triangulation of placement centers."""
    n = len(placements)
    if n < 2:
        return []
    if n == 2:
        return [(0, 1)]
    centers = np.array([
        (p.x + p.photo.width / 2, p.y + p.photo.height / 2)
        for p in placements
    ])
    try:
        tri = Delaunay(centers)
    except QhullError:
        # Collinear points: connect consecutive points along the line
        diffs = centers - centers[0]
        projections = np.dot(diffs, diffs[-1] if np.any(diffs[-1]) else np.array([1.0, 0.0]))
        order = np.argsort(projections)
        return sorted(
            (min(int(order[i]), int(order[i + 1])), max(int(order[i]), int(order[i + 1])))
            for i in range(n - 1)
        )
    edges: set[tuple[int, int]] = set()
    for simplex in tri.simplices:
        for i in range(len(simplex)):
            for j in range(i + 1, len(simplex)):
                a, b = sorted((simplex[i], simplex[j]))
                edges.add((a, b))
    return sorted(edges)


def gap_variance(
    placements: list[Placement], adjacency: list[tuple[int, int]]
) -> float:
    """Return the population variance of edge-to-edge distances."""
    distances = [edge_distance(placements[i], placements[j]) for i, j in adjacency]
    mean = sum(distances) / len(distances)
    return sum((d - mean) ** 2 for d in distances) / len(distances)
