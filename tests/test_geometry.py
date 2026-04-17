import pytest

from gallery_wall_organiser.geometry import (
    build_adjacency,
    edge_distance,
    gap_variance,
    intersection_area,
    is_within_bounds,
    overlaps_obstacle,
    placements_overlap,
    quadrant_areas,
    quadrant_imbalance,
    rectangles_overlap,
)
from gallery_wall_organiser.models import Layout, Obstacle, Photo, Placement, Wall


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


class TestEdgeDistanceHorizontallySeparated:
    def test_same_row_gap_between(self):
        # p1: x=[0,100], y=[0,100]; p2: x=[150,250], y=[0,100]
        # horizontal gap = 150 - 100 = 50; vertically aligned → distance = 50
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=150, y=0)

        assert edge_distance(p1, p2) == 50.0

    def test_symmetry(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=150, y=0)

        assert edge_distance(p1, p2) == edge_distance(p2, p1)

    def test_different_widths(self):
        # p1: x=[0,200], y=[0,100]; p2: x=[250,300], y=[0,100]
        # horizontal gap = 250 - 200 = 50
        p1 = Placement(photo=Photo(height=100, width=200), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=50), x=250, y=0)

        assert edge_distance(p1, p2) == 50.0


class TestEdgeDistanceVerticallySeparated:
    def test_same_column_gap_between(self):
        # p1: x=[0,100], y=[0,100]; p2: x=[0,100], y=[200,300]
        # vertical gap = 200 - 100 = 100; horizontally aligned → distance = 100
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=0, y=200)

        assert edge_distance(p1, p2) == 100.0

    def test_symmetry(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=0, y=200)

        assert edge_distance(p1, p2) == edge_distance(p2, p1)

    def test_different_heights(self):
        # p1: x=[0,100], y=[0,50]; p2: x=[0,100], y=[80,280]
        # vertical gap = 80 - 50 = 30
        p1 = Placement(photo=Photo(height=50, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=200, width=100), x=0, y=80)

        assert edge_distance(p1, p2) == 30.0


class TestEdgeDistanceDiagonallySeparated:
    def test_diagonal_separation(self):
        # p1: x=[0,100], y=[0,100]; p2: x=[200,300], y=[200,300]
        # horizontal gap = 200 - 100 = 100; vertical gap = 200 - 100 = 100
        # distance = sqrt(100^2 + 100^2) ≈ 141.42
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=200, y=200)

        assert edge_distance(p1, p2) == pytest.approx(141.4213562373095)

    def test_diagonal_symmetry(self):
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=200, y=200)

        assert edge_distance(p1, p2) == edge_distance(p2, p1)

    def test_unequal_gaps(self):
        # p1: x=[0,100], y=[0,100]; p2: x=[140,240], y=[200,300]
        # horizontal gap = 140 - 100 = 40; vertical gap = 200 - 100 = 100
        # distance = sqrt(40^2 + 100^2) = sqrt(1600 + 10000) = sqrt(11600)
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=140, y=200)

        assert edge_distance(p1, p2) == pytest.approx(107.7032961426901)

    def test_opposite_diagonal(self):
        # p2 is top-right of p1: separated both horizontally and vertically
        # p1: x=[100,200], y=[200,300]; p2: x=[300,400], y=[0,100]
        # horizontal gap = 300 - 200 = 100; vertical gap = 200 - 100 = 100
        # distance = sqrt(100^2 + 100^2)
        p1 = Placement(photo=Photo(height=100, width=100), x=100, y=200)
        p2 = Placement(photo=Photo(height=100, width=100), x=300, y=0)

        assert edge_distance(p1, p2) == pytest.approx(141.4213562373095)


class TestEdgeDistanceAdjacent:
    def test_adjacent_horizontally(self):
        # p1 right edge == p2 left edge → distance = 0
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=100, y=0)

        assert edge_distance(p1, p2) == 0.0

    def test_adjacent_vertically(self):
        # p1 bottom edge == p2 top edge → distance = 0
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=0, y=100)

        assert edge_distance(p1, p2) == 0.0

    def test_adjacent_at_corner(self):
        # touching at single corner → distance = 0
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=100, y=100)

        assert edge_distance(p1, p2) == 0.0

    def test_overlapping_returns_zero(self):
        # overlapping placements should also return 0
        p1 = Placement(photo=Photo(height=100, width=100), x=0, y=0)
        p2 = Placement(photo=Photo(height=100, width=100), x=50, y=50)

        assert edge_distance(p1, p2) == 0.0


class TestBuildAdjacencyTwoPlacements:
    def test_returns_single_edge(self):
        placements = [
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
            Placement(photo=Photo(height=100, width=100), x=300, y=0),
        ]

        result = build_adjacency(placements)

        assert result == [(0, 1)]

    def test_edge_indices_are_sorted(self):
        # Each tuple should have smaller index first
        placements = [
            Placement(photo=Photo(height=100, width=100), x=300, y=0),
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
        ]

        result = build_adjacency(placements)

        for i, j in result:
            assert i < j


class TestBuildAdjacencyThreePlacements:
    def test_triangle_returns_three_edges(self):
        # Three placements forming a triangle — Delaunay connects all three
        placements = [
            Placement(photo=Photo(height=50, width=50), x=0, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=0),
            Placement(photo=Photo(height=50, width=50), x=200, y=400),
        ]

        result = build_adjacency(placements)

        assert len(result) == 3
        assert (0, 1) in result
        assert (0, 2) in result
        assert (1, 2) in result

    def test_collinear_returns_two_edges(self):
        # Three collinear placements — middle connects to both ends, ends not connected
        placements = [
            Placement(photo=Photo(height=50, width=50), x=0, y=0),
            Placement(photo=Photo(height=50, width=50), x=200, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=0),
        ]

        result = build_adjacency(placements)

        assert len(result) == 2
        assert (0, 1) in result
        assert (1, 2) in result

    def test_no_duplicate_edges(self):
        placements = [
            Placement(photo=Photo(height=50, width=50), x=0, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=0),
            Placement(photo=Photo(height=50, width=50), x=200, y=400),
        ]

        result = build_adjacency(placements)

        assert len(result) == len(set(result))


class TestBuildAdjacencyFourPlacements:
    def test_square_returns_five_edges(self):
        # Four placements at corners of a square — Delaunay produces 4 outer + 1 diagonal = 5
        placements = [
            Placement(photo=Photo(height=50, width=50), x=0, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=400),
            Placement(photo=Photo(height=50, width=50), x=0, y=400),
        ]

        result = build_adjacency(placements)

        # 4 edges of the square + 1 diagonal = 5
        assert len(result) == 5

    def test_square_contains_all_perimeter_edges(self):
        placements = [
            Placement(photo=Photo(height=50, width=50), x=0, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=400),
            Placement(photo=Photo(height=50, width=50), x=0, y=400),
        ]

        result = build_adjacency(placements)

        assert (0, 1) in result
        assert (1, 2) in result
        assert (2, 3) in result
        assert (0, 3) in result

    def test_returns_list_of_tuples(self):
        placements = [
            Placement(photo=Photo(height=50, width=50), x=0, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=0),
            Placement(photo=Photo(height=50, width=50), x=400, y=400),
            Placement(photo=Photo(height=50, width=50), x=0, y=400),
        ]

        result = build_adjacency(placements)

        assert isinstance(result, list)
        for edge in result:
            assert isinstance(edge, tuple)
            assert len(edge) == 2


class TestGapVarianceEqualGaps:
    def test_two_pairs_equal_gaps(self):
        # Three placements in a row, equal 50-unit gaps between them
        # p0: x=[0,100], p1: x=[150,250], p2: x=[300,400] — all y=[0,100]
        # edge_distance(p0,p1) = 50, edge_distance(p1,p2) = 50
        # variance of [50, 50] = 0.0
        placements = [
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
            Placement(photo=Photo(height=100, width=100), x=150, y=0),
            Placement(photo=Photo(height=100, width=100), x=300, y=0),
        ]
        adjacency = [(0, 1), (1, 2)]

        assert gap_variance(placements, adjacency) == 0.0

    def test_identical_placements_zero_gaps(self):
        # Two overlapping placements — both gaps are 0 → variance = 0
        placements = [
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
        ]
        adjacency = [(0, 1)]

        assert gap_variance(placements, adjacency) == 0.0


class TestGapVarianceMixedGaps:
    def test_two_different_gaps(self):
        # p0: x=[0,100], p1: x=[150,250], p2: x=[400,500] — all y=[0,100]
        # edge_distance(p0,p1) = 50, edge_distance(p1,p2) = 150
        # mean = 100, variance = ((50-100)^2 + (150-100)^2) / 2 = (2500+2500)/2 = 2500.0
        placements = [
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
            Placement(photo=Photo(height=100, width=100), x=150, y=0),
            Placement(photo=Photo(height=100, width=100), x=400, y=0),
        ]
        adjacency = [(0, 1), (1, 2)]

        assert gap_variance(placements, adjacency) == pytest.approx(2500.0)

    def test_three_different_gaps(self):
        # p0: x=[0,100] y=[0,100], p1: x=[200,300] y=[0,100], p2: x=[500,600] y=[0,100]
        # edge_distance(p0,p1) = 100, edge_distance(p1,p2) = 200, edge_distance(p0,p2) = 400
        # mean = (100+200+400)/3 ≈ 233.333
        # var = ((100-233.333)^2 + (200-233.333)^2 + (400-233.333)^2) / 3
        #     = (17777.78 + 1111.11 + 27777.78) / 3 = 46666.67 / 3 ≈ 15555.56
        placements = [
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
            Placement(photo=Photo(height=100, width=100), x=200, y=0),
            Placement(photo=Photo(height=100, width=100), x=500, y=0),
        ]
        adjacency = [(0, 1), (1, 2), (0, 2)]

        assert gap_variance(placements, adjacency) == pytest.approx(15555.555555555555)


class TestGapVarianceSinglePair:
    def test_single_edge_returns_zero(self):
        # Variance of a single value is 0
        placements = [
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
            Placement(photo=Photo(height=100, width=100), x=200, y=0),
        ]
        adjacency = [(0, 1)]

        assert gap_variance(placements, adjacency) == 0.0

    def test_returns_float(self):
        placements = [
            Placement(photo=Photo(height=100, width=100), x=0, y=0),
            Placement(photo=Photo(height=100, width=100), x=200, y=0),
        ]
        adjacency = [(0, 1)]

        assert isinstance(gap_variance(placements, adjacency), float)


class TestIntersectionAreaFullOverlap:
    def test_identical_rectangles(self):
        r = (0, 0, 100, 200)

        assert intersection_area(r, r) == 20000.0

    def test_is_symmetric(self):
        r1 = (10, 20, 100, 200)
        r2 = (50, 60, 80, 120)

        assert intersection_area(r1, r2) == intersection_area(r2, r1)


class TestIntersectionAreaPartialOverlap:
    def test_overlap_from_right(self):
        # r1: x=[0,100], y=[0,100]; r2: x=[60,160], y=[0,100]
        # overlap: x=[60,100], y=[0,100] → 40 * 100 = 4000
        r1 = (0, 0, 100, 100)
        r2 = (60, 0, 100, 100)

        assert intersection_area(r1, r2) == 4000.0

    def test_overlap_from_below(self):
        # r1: x=[0,100], y=[0,100]; r2: x=[0,100], y=[70,170]
        # overlap: x=[0,100], y=[70,100] → 100 * 30 = 3000
        r1 = (0, 0, 100, 100)
        r2 = (0, 70, 100, 100)

        assert intersection_area(r1, r2) == 3000.0

    def test_overlap_diagonal(self):
        # r1: x=[0,100], y=[0,100]; r2: x=[50,150], y=[50,150]
        # overlap: x=[50,100], y=[50,100] → 50 * 50 = 2500
        r1 = (0, 0, 100, 100)
        r2 = (50, 50, 100, 100)

        assert intersection_area(r1, r2) == 2500.0


class TestIntersectionAreaNoOverlap:
    def test_separated_horizontally(self):
        r1 = (0, 0, 100, 100)
        r2 = (200, 0, 100, 100)

        assert intersection_area(r1, r2) == 0.0

    def test_separated_vertically(self):
        r1 = (0, 0, 100, 100)
        r2 = (0, 200, 100, 100)

        assert intersection_area(r1, r2) == 0.0

    def test_touching_edges(self):
        # Touching but not overlapping → 0
        r1 = (0, 0, 100, 100)
        r2 = (100, 0, 100, 100)

        assert intersection_area(r1, r2) == 0.0

    def test_touching_at_corner(self):
        r1 = (0, 0, 100, 100)
        r2 = (100, 100, 100, 100)

        assert intersection_area(r1, r2) == 0.0


class TestIntersectionAreaContainment:
    def test_r2_inside_r1(self):
        # r1: x=[0,200], y=[0,200]; r2: x=[50,100], y=[50,100]
        # overlap = entire r2 → 50 * 50 = 2500
        r1 = (0, 0, 200, 200)
        r2 = (50, 50, 50, 50)

        assert intersection_area(r1, r2) == 2500.0

    def test_r1_inside_r2(self):
        # overlap = entire r1 → 50 * 50 = 2500
        r1 = (50, 50, 50, 50)
        r2 = (0, 0, 200, 200)

        assert intersection_area(r1, r2) == 2500.0

    def test_returns_float(self):
        r1 = (0, 0, 100, 100)
        r2 = (25, 25, 50, 50)

        assert isinstance(intersection_area(r1, r2), float)


class TestQuadrantAreasCenteredPhoto:
    def test_centered_photo_spans_all_four_equally(self):
        # Wall 200x200, eye_level=100 → center=(100,100)
        # Photo 100x100 placed at (50,50) → x=[50,150], y=[50,150]
        # Each quadrant gets a 50x50 slice = 2500
        wall = Wall(height=200, width=200)
        photo = Photo(height=100, width=100)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=photo, x=50, y=50)],
            obstacles=[],
            d=0,
            eye_level=100,
        )

        result = quadrant_areas(layout)

        assert result == (2500.0, 2500.0, 2500.0, 2500.0)

    def test_returns_tuple_of_four_floats(self):
        wall = Wall(height=200, width=200)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=50), x=0, y=0)],
            obstacles=[],
            d=0,
            eye_level=100,
        )

        result = quadrant_areas(layout)

        assert isinstance(result, tuple)
        assert len(result) == 4
        assert all(isinstance(a, float) for a in result)


class TestQuadrantAreasInOneQuadrant:
    def test_photo_entirely_in_top_left(self):
        # Wall 400x400, eye_level=200, center=200
        # Photo 50x50 at (10,10) → x=[10,60], y=[10,60] — all in TL
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=50), x=10, y=10)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_areas(layout) == (2500.0, 0.0, 0.0, 0.0)

    def test_photo_entirely_in_top_right(self):
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=50), x=300, y=10)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_areas(layout) == (0.0, 2500.0, 0.0, 0.0)

    def test_photo_entirely_in_bottom_left(self):
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=50), x=10, y=300)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_areas(layout) == (0.0, 0.0, 2500.0, 0.0)

    def test_photo_entirely_in_bottom_right(self):
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=50), x=300, y=300)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_areas(layout) == (0.0, 0.0, 0.0, 2500.0)


class TestQuadrantAreasMultiplePhotos:
    def test_two_photos_in_different_quadrants(self):
        # Wall 400x400, eye_level=200
        # Photo A 50x50 at (10,10) in TL → 2500
        # Photo B 80x60 at (300,300) in BR → 4800
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[
                Placement(photo=Photo(height=50, width=50), x=10, y=10),
                Placement(photo=Photo(height=80, width=60), x=300, y=300),
            ],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_areas(layout) == (2500.0, 0.0, 0.0, 4800.0)

    def test_no_placements(self):
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_areas(layout) == (0.0, 0.0, 0.0, 0.0)

    def test_photo_spanning_two_quadrants_horizontally(self):
        # Wall 400x400, eye_level=200, center=200
        # Photo 50x100 at (150,10) → x=[150,250], y=[10,60]
        # TL: x=[150,200] × y=[10,60] = 50×50 = 2500
        # TR: x=[200,250] × y=[10,60] = 50×50 = 2500
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=100), x=150, y=10)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_areas(layout) == (2500.0, 2500.0, 0.0, 0.0)


class TestQuadrantImbalanceBalanced:
    def test_equal_area_in_all_quadrants(self):
        # Centered photo splits equally → imbalance = 0
        wall = Wall(height=200, width=200)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=100, width=100), x=50, y=50)],
            obstacles=[],
            d=0,
            eye_level=100,
        )

        assert quadrant_imbalance(layout) == 0.0

    def test_no_placements(self):
        # All quadrants have 0 area → imbalance = 0
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_imbalance(layout) == 0.0


class TestQuadrantImbalancePositive:
    def test_all_area_in_one_quadrant(self):
        # 50x50 photo entirely in TL → areas=(2500,0,0,0)
        # imbalance = 2500 - 0 = 2500
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=50), x=10, y=10)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_imbalance(layout) == 2500.0

    def test_area_in_two_quadrants(self):
        # Photo spanning TL and TR equally: areas=(2500,2500,0,0)
        # imbalance = 2500 - 0 = 2500
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=100), x=150, y=10)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_imbalance(layout) == 2500.0

    def test_unequal_photos_in_different_quadrants(self):
        # TL=2500 (50x50), BR=4800 (80x60) → max=4800, min=0 → imbalance=4800
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[
                Placement(photo=Photo(height=50, width=50), x=10, y=10),
                Placement(photo=Photo(height=80, width=60), x=300, y=300),
            ],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert quadrant_imbalance(layout) == 4800.0

    def test_returns_float(self):
        wall = Wall(height=400, width=400)
        layout = Layout(
            wall=wall,
            placements=[Placement(photo=Photo(height=50, width=50), x=10, y=10)],
            obstacles=[],
            d=0,
            eye_level=200,
        )

        assert isinstance(quadrant_imbalance(layout), float)

