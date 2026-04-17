import pytest

from gallery_wall_organiser.geometry import (
    is_within_bounds,
    overlaps_obstacle,
    placements_overlap,
    rectangles_overlap,
)
from gallery_wall_organiser.models import Obstacle, Photo, Placement, Wall


# Each rectangle is (x, y, width, height) where (x, y) is the top-left corner.


class TestRectanglesOverlapOverlapping:
    def test_partial_overlap_from_right(self):
        r1 = (0, 0, 100, 100)
        r2 = (50, 0, 100, 100)

        assert rectangles_overlap(r1, r2) is True

    def test_partial_overlap_from_below(self):
        r1 = (0, 0, 100, 100)
        r2 = (0, 50, 100, 100)

        assert rectangles_overlap(r1, r2) is True

    def test_partial_overlap_diagonal(self):
        r1 = (0, 0, 100, 100)
        r2 = (50, 50, 100, 100)

        assert rectangles_overlap(r1, r2) is True

    def test_overlap_is_symmetric(self):
        r1 = (0, 0, 100, 100)
        r2 = (50, 50, 100, 100)

        assert rectangles_overlap(r1, r2) == rectangles_overlap(r2, r1)


class TestRectanglesOverlapFullyContained:
    def test_r2_fully_inside_r1(self):
        r1 = (0, 0, 200, 200)
        r2 = (50, 50, 50, 50)

        assert rectangles_overlap(r1, r2) is True

    def test_r1_fully_inside_r2(self):
        r1 = (50, 50, 50, 50)
        r2 = (0, 0, 200, 200)

        assert rectangles_overlap(r1, r2) is True

    def test_identical_rectangles(self):
        r1 = (10, 10, 80, 80)
        r2 = (10, 10, 80, 80)

        assert rectangles_overlap(r1, r2) is True


class TestRectanglesOverlapTouchingEdges:
    def test_touching_right_edge(self):
        r1 = (0, 0, 100, 100)
        r2 = (100, 0, 100, 100)

        assert rectangles_overlap(r1, r2) is False

    def test_touching_bottom_edge(self):
        r1 = (0, 0, 100, 100)
        r2 = (0, 100, 100, 100)

        assert rectangles_overlap(r1, r2) is False

    def test_touching_left_edge(self):
        r1 = (100, 0, 100, 100)
        r2 = (0, 0, 100, 100)

        assert rectangles_overlap(r1, r2) is False

    def test_touching_top_edge(self):
        r1 = (0, 100, 100, 100)
        r2 = (0, 0, 100, 100)

        assert rectangles_overlap(r1, r2) is False

    def test_touching_at_single_corner(self):
        r1 = (0, 0, 100, 100)
        r2 = (100, 100, 100, 100)

        assert rectangles_overlap(r1, r2) is False


class TestRectanglesOverlapNonOverlapping:
    def test_separated_horizontally(self):
        r1 = (0, 0, 100, 100)
        r2 = (200, 0, 100, 100)

        assert rectangles_overlap(r1, r2) is False

    def test_separated_vertically(self):
        r1 = (0, 0, 100, 100)
        r2 = (0, 200, 100, 100)

        assert rectangles_overlap(r1, r2) is False

    def test_separated_diagonally(self):
        r1 = (0, 0, 100, 100)
        r2 = (200, 200, 100, 100)

        assert rectangles_overlap(r1, r2) is False

    def test_non_overlap_is_symmetric(self):
        r1 = (0, 0, 100, 100)
        r2 = (200, 0, 100, 100)

        assert rectangles_overlap(r1, r2) == rectangles_overlap(r2, r1)


class TestIsWithinBounds:
    def test_fully_inside_wall(self):
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=100, y=100)

        assert is_within_bounds(placement, wall) is True

    def test_exactly_on_boundary(self):
        # Photo fills the wall exactly — all edges coincide
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=2400, width=1800), x=0, y=0)

        assert is_within_bounds(placement, wall) is True

    def test_touching_right_edge_exactly(self):
        # right == wall.width — still within bounds
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=1500, y=0)  # 1500 + 300 = 1800

        assert is_within_bounds(placement, wall) is True

    def test_touching_bottom_edge_exactly(self):
        # bottom == wall.height — still within bounds
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=0, y=2000)  # 2000 + 400 = 2400

        assert is_within_bounds(placement, wall) is True

    def test_placed_at_origin(self):
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=0, y=0)

        assert is_within_bounds(placement, wall) is True

    def test_partially_outside_right_edge(self):
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=1600, y=0)  # 1600 + 300 = 1900 > 1800

        assert is_within_bounds(placement, wall) is False

    def test_partially_outside_bottom_edge(self):
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=0, y=2100)  # 2100 + 400 = 2500 > 2400

        assert is_within_bounds(placement, wall) is False

    def test_partially_outside_left_edge(self):
        # x is negative — left edge beyond wall boundary
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=-10, y=0)

        assert is_within_bounds(placement, wall) is False

    def test_partially_outside_top_edge(self):
        # y is negative — top edge beyond wall boundary
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=0, y=-10)

        assert is_within_bounds(placement, wall) is False

    def test_entirely_outside_wall(self):
        wall = Wall(height=2400, width=1800)
        placement = Placement(photo=Photo(height=400, width=300), x=2000, y=0)

        assert is_within_bounds(placement, wall) is False


class TestOverlapsObstacle:
    def test_overlap(self):
        placement = Placement(photo=Photo(height=400, width=300), x=50, y=50)
        obstacle = Obstacle(x=100, y=100, height=80, width=60)

        assert overlaps_obstacle(placement, obstacle) is True

    def test_placement_fully_covers_obstacle(self):
        placement = Placement(photo=Photo(height=400, width=300), x=0, y=0)
        obstacle = Obstacle(x=50, y=50, height=10, width=10)

        assert overlaps_obstacle(placement, obstacle) is True

    def test_obstacle_fully_covers_placement(self):
        placement = Placement(photo=Photo(height=50, width=50), x=100, y=100)
        obstacle = Obstacle(x=0, y=0, height=500, width=500)

        assert overlaps_obstacle(placement, obstacle) is True

    def test_adjacent_on_right_edge(self):
        # placement right == obstacle left — touching, not overlapping
        placement = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        obstacle = Obstacle(x=100, y=0, height=100, width=50)

        assert overlaps_obstacle(placement, obstacle) is False

    def test_adjacent_on_bottom_edge(self):
        # placement bottom == obstacle top — touching, not overlapping
        placement = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        obstacle = Obstacle(x=0, y=100, height=50, width=100)

        assert overlaps_obstacle(placement, obstacle) is False

    def test_adjacent_on_left_edge(self):
        # obstacle right == placement left
        placement = Placement(photo=Photo(height=100, width=100), x=100, y=0)
        obstacle = Obstacle(x=0, y=0, height=100, width=100)

        assert overlaps_obstacle(placement, obstacle) is False

    def test_adjacent_on_top_edge(self):
        # obstacle bottom == placement top
        placement = Placement(photo=Photo(height=100, width=100), x=0, y=100)
        obstacle = Obstacle(x=0, y=0, height=100, width=100)

        assert overlaps_obstacle(placement, obstacle) is False

    def test_clearly_separated(self):
        placement = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        obstacle = Obstacle(x=500, y=500, height=50, width=50)

        assert overlaps_obstacle(placement, obstacle) is False


class TestPlacementsOverlap:
    def test_overlapping(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=50, y=50)

        assert placements_overlap(p1, p2) is True

    def test_one_contains_the_other(self):
        p1 = Placement(photo=Photo(height=300, width=300), x=0, y=0)
        p2 = Placement(photo=Photo(height=50, width=50), x=100, y=100)

        assert placements_overlap(p1, p2) is True

    def test_identical_position_and_size(self):
        photo = Photo(height=100, width=100)
        p1 = Placement(photo=photo, x=50, y=50)
        p2 = Placement(photo=photo, x=50, y=50)

        assert placements_overlap(p1, p2) is True

    def test_overlap_is_symmetric(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=50, y=50)

        assert placements_overlap(p1, p2) == placements_overlap(p2, p1)

    def test_adjacent_horizontally(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=100, y=0)

        assert placements_overlap(p1, p2) is False

    def test_adjacent_vertically(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=0, y=100)

        assert placements_overlap(p1, p2) is False

    def test_adjacent_at_corner(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=100, y=100)

        assert placements_overlap(p1, p2) is False

    def test_separated_horizontally(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=300, y=0)

        assert placements_overlap(p1, p2) is False

    def test_separated_vertically(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=0, y=300)

        assert placements_overlap(p1, p2) is False

    def test_different_sized_photos_separated(self):
        p1 = Placement(photo=Photo(height=200, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=50, width=300), x=200, y=0)

        assert placements_overlap(p1, p2) is False

