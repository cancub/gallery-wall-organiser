from dataclasses import dataclass


def _positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


@dataclass
class _Dimensions:
    height: float
    width: float

    def __post_init__(self) -> None:
        _positive(self.height, "height")
        _positive(self.width, "width")


@dataclass
class Wall(_Dimensions):
    pass


@dataclass
class Photo(_Dimensions):
    pass


@dataclass
class Obstacle:
    x: float
    y: float
    height: float
    width: float

    def __post_init__(self) -> None:
        _positive(self.height, "height")
        _positive(self.width, "width")
