import matplotlib
import matplotlib.patches as mpatches
import pytest
from matplotlib.figure import Figure

from gallery_wall_organiser.models import Layout, Obstacle, Photo, Placement, Wall
from gallery_wall_organiser.visualizer import render

matplotlib.use("Agg")


def _layout(num_photos=2, num_obstacles=1):
    wall = Wall(height=2000, width=3000)
    photos = [Photo(height=300, width=400) for _ in range(num_photos)]
    placements = [
        Placement(photo=photos[i], x=100 + i * 500, y=200) for i in range(num_photos)
    ]
    obstacles = [
        Obstacle(x=1400, y=800, height=200, width=300) for _ in range(num_obstacles)
    ]
    return Layout(wall=wall, placements=placements, obstacles=obstacles, d=50, eye_level=1450)


class TestRenderReturnType:
    def test_returns_figure(self):
        layout = _layout()
        result = render(layout)
        assert isinstance(result, Figure)


class TestRenderAxes:
    def test_has_exactly_one_axes(self):
        layout = _layout()
        fig = render(layout)
        assert len(fig.axes) == 1

    def test_axes_limits_match_wall(self):
        layout = _layout()
        fig = render(layout)
        ax = fig.axes[0]
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        assert x_min == pytest.approx(0)
        assert x_max == pytest.approx(layout.wall.width)
        assert y_min == pytest.approx(0)
        assert y_max == pytest.approx(layout.wall.height)


class TestRenderRectanglePatchCount:
    def test_patch_count_equals_placements_plus_obstacles(self):
        layout = _layout(num_photos=2, num_obstacles=1)
        fig = render(layout)
        ax = fig.axes[0]
        rectangles = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
        assert len(rectangles) == len(layout.placements) + len(layout.obstacles)

    def test_patch_count_no_obstacles(self):
        layout = _layout(num_photos=3, num_obstacles=0)
        fig = render(layout)
        ax = fig.axes[0]
        rectangles = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
        assert len(rectangles) == 3

    def test_patch_count_no_placements(self):
        wall = Wall(height=2000, width=3000)
        layout = Layout(
            wall=wall,
            placements=[],
            obstacles=[Obstacle(x=500, y=500, height=200, width=300)],
            d=50,
            eye_level=1450,
        )
        fig = render(layout)
        ax = fig.axes[0]
        rectangles = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
        assert len(rectangles) == 1

    def test_patch_count_many_placements_many_obstacles(self):
        layout = _layout(num_photos=5, num_obstacles=3)
        fig = render(layout)
        ax = fig.axes[0]
        rectangles = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
        assert len(rectangles) == 8
