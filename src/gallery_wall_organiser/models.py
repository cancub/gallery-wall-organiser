from dataclasses import dataclass


def _positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


def _validate_dimensions(height: float, width: float) -> None:
    _positive(height, "height")
    _positive(width, "width")


@dataclass
class _Dimensions:
    height: float
    width: float

    def __post_init__(self) -> None:
        _validate_dimensions(self.height, self.width)


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
        _validate_dimensions(self.height, self.width)


@dataclass
class Placement:
    photo: Photo
    x: float
    y: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def right(self) -> float:
        return self.x + self.photo.width

    @property
    def bottom(self) -> float:
        return self.y + self.photo.height
