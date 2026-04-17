import pytest

from gallery_wall_organiser.geometry import rectangles_overlap


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
