from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gallery-wall-organiser",
        description="Automatically arrange photos on a gallery wall for visual balance.",
    )
    parser.add_argument("--wall", nargs=2, type=float, metavar=("H", "W"), required=True)
    parser.add_argument("--photos", nargs="+", type=float, metavar="DIM", required=True)
    parser.add_argument("--obstacles", nargs="+", type=float, metavar="DIM", default=[])
    parser.add_argument("--eye-level", type=float, default=1450.0)

    args = parser.parse_args()
    print(f"wall={args.wall}, photos={args.photos}, obstacles={args.obstacles}, eye-level={args.eye_level}")


if __name__ == "__main__":
    main()
