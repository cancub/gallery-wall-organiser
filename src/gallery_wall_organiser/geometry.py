from __future__ import annotations

from typing import TYPE_CHECKING

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
