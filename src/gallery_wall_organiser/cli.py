from __future__ import annotations

import argparse
from typing import Sequence

from matplotlib.figure import Figure

from gallery_wall_organiser.models import Obstacle, Photo, Wall
from gallery_wall_organiser.solver import optimize
from gallery_wall_organiser.visualizer import render


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gallery-wall-organiser",
        description="Automatically arrange photos on a gallery wall for visual balance.",
    )
    parser.add_argument("--wall", nargs=2, type=float, metavar=("H", "W"), required=True)
    parser.add_argument("--photos", nargs="+", type=float, metavar="DIM", required=True)
    parser.add_argument("--obstacles", nargs="+", type=float, metavar="DIM", default=[])
    parser.add_argument("--eye-level", type=float, default=1450.0)
    return parser


def _chunked(values: list[float], size: int) -> list[list[float]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def _require_even(parser: argparse.ArgumentParser, values: list[float], flag: str, group_size: int) -> None:
    if len(values) % group_size != 0:
        parser.error(f"{flag} requires groups of {group_size} values")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = _build_parser()
    args = parser.parse_args(argv)

    args.wall = Wall(height=args.wall[0], width=args.wall[1])

    _require_even(parser, args.photos, "--photos", 2)
    args.photos = [Photo(height=h, width=w) for h, w in _chunked(args.photos, 2)]

    _require_even(parser, args.obstacles, "--obstacles", 4)
    args.obstacles = [
        Obstacle(x=x, y=y, height=h, width=w) for x, y, h, w in _chunked(args.obstacles, 4)
    ]

    return args


def run(argv: Sequence[str] | None = None) -> Figure:
    args = parse_args(argv)
    layout = optimize(args.wall, args.photos, args.obstacles, args.eye_level, max_iterations=500, seed=0)
    return render(layout)


def main() -> None:
    run()


if __name__ == "__main__":
    main()
