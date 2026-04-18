import matplotlib
import pytest
from matplotlib.figure import Figure

from gallery_wall_organiser.cli import run

matplotlib.use("Agg")

_SMALL_WALL_ARGS = [
    "--wall", "2000", "3000",
    "--photos", "300", "400", "250", "350", "400", "500",
    "--obstacles", "1200", "800", "200", "300",
    "--eye-level", "1450",
]


class TestRunReturnType:
    def test_returns_figure(self):
        result = run(_SMALL_WALL_ARGS)
        assert isinstance(result, Figure)


class TestRunCompletes:
    def test_does_not_raise(self):
        run(_SMALL_WALL_ARGS)

    def test_without_obstacles_does_not_raise(self):
        run([
            "--wall", "2000", "3000",
            "--photos", "300", "400", "250", "350", "400", "500",
        ])

    def test_default_eye_level_does_not_raise(self):
        run([
            "--wall", "2000", "3000",
            "--photos", "300", "400", "250", "350", "400", "500",
            "--obstacles", "1200", "800", "200", "300",
        ])


class TestRunFigureContent:
    def test_figure_has_one_axes(self):
        fig = run(_SMALL_WALL_ARGS)
        assert len(fig.axes) == 1

    def test_figure_has_rectangle_patches_for_photos_and_obstacles(self):
        import matplotlib.patches as mpatches
        fig = run(_SMALL_WALL_ARGS)
        ax = fig.axes[0]
        rectangles = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
        # 3 photos + 1 obstacle
        assert len(rectangles) == 4
