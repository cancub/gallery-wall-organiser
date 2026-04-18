from __future__ import annotations

import argparse
from typing import Sequence

from gallery_wall_organiser.models import Obstacle, Photo, Wall


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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = _build_parser()
    args = parser.parse_args(argv)

    args.wall = Wall(height=args.wall[0], width=args.wall[1])

    if len(args.photos) % 2 != 0:
        parser.error("--photos requires an even number of values (H W pairs)")
    args.photos = [Photo(height=h, width=w) for h, w in _chunked(args.photos, 2)]

    if len(args.obstacles) % 4 != 0:
        parser.error("--obstacles requires groups of 4 values (X Y H W)")
    args.obstacles = [
        Obstacle(x=x, y=y, height=h, width=w) for x, y, h, w in _chunked(args.obstacles, 4)
    ]

    return args


def main() -> None:
    args = parse_args()
    print(f"wall={args.wall}, photos={args.photos}, obstacles={args.obstacles}, eye-level={args.eye_level}")


if __name__ == "__main__":
    main()
