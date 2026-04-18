import pytest

from gallery_wall_organiser.cli import parse_args
from gallery_wall_organiser.models import Obstacle, Photo, Wall


class TestWallArgument:
    def test_wall_parsed_as_wall_object(self):
        result = parse_args(["--wall", "2000", "3000", "--photos", "300", "400"])
        assert isinstance(result.wall, Wall)

    def test_wall_height_and_width(self):
        result = parse_args(["--wall", "2000", "3000", "--photos", "300", "400"])
        assert result.wall.height == 2000.0
        assert result.wall.width == 3000.0

    def test_wall_missing_raises(self):
        with pytest.raises(SystemExit):
            parse_args(["--photos", "300", "400"])


class TestPhotosArgument:
    def test_single_photo_parsed_as_list_of_photo(self):
        result = parse_args(["--wall", "2000", "3000", "--photos", "300", "400"])
        assert len(result.photos) == 1
        assert isinstance(result.photos[0], Photo)

    def test_single_photo_dimensions(self):
        result = parse_args(["--wall", "2000", "3000", "--photos", "300", "400"])
        assert result.photos[0].height == 300.0
        assert result.photos[0].width == 400.0

    def test_multiple_photos(self):
        result = parse_args([
            "--wall", "2000", "3000",
            "--photos", "300", "400", "500", "600",
        ])
        assert len(result.photos) == 2
        assert result.photos[0].height == 300.0
        assert result.photos[0].width == 400.0
        assert result.photos[1].height == 500.0
        assert result.photos[1].width == 600.0

    def test_odd_number_of_photo_dims_raises(self):
        with pytest.raises((SystemExit, ValueError)):
            parse_args(["--wall", "2000", "3000", "--photos", "300"])

    def test_photos_missing_raises(self):
        with pytest.raises(SystemExit):
            parse_args(["--wall", "2000", "3000"])


class TestObstaclesArgument:
    def test_no_obstacles_defaults_to_empty_list(self):
        result = parse_args(["--wall", "2000", "3000", "--photos", "300", "400"])
        assert result.obstacles == []

    def test_single_obstacle_parsed_as_list_of_obstacle(self):
        result = parse_args([
            "--wall", "2000", "3000",
            "--photos", "300", "400",
            "--obstacles", "100", "200", "150", "250",
        ])
        assert len(result.obstacles) == 1
        assert isinstance(result.obstacles[0], Obstacle)

    def test_single_obstacle_fields(self):
        result = parse_args([
            "--wall", "2000", "3000",
            "--photos", "300", "400",
            "--obstacles", "100", "200", "150", "250",
        ])
        o = result.obstacles[0]
        assert o.x == 100.0
        assert o.y == 200.0
        assert o.height == 150.0
        assert o.width == 250.0

    def test_multiple_obstacles(self):
        result = parse_args([
            "--wall", "2000", "3000",
            "--photos", "300", "400",
            "--obstacles", "100", "200", "150", "250", "500", "600", "80", "90",
        ])
        assert len(result.obstacles) == 2

    def test_odd_number_of_obstacle_dims_raises(self):
        with pytest.raises((SystemExit, ValueError)):
            parse_args([
                "--wall", "2000", "3000",
                "--photos", "300", "400",
                "--obstacles", "100", "200", "150",
            ])


class TestEyeLevelArgument:
    def test_eye_level_defaults_to_1450(self):
        result = parse_args(["--wall", "2000", "3000", "--photos", "300", "400"])
        assert result.eye_level == 1450.0

    def test_eye_level_can_be_set(self):
        result = parse_args([
            "--wall", "2000", "3000",
            "--photos", "300", "400",
            "--eye-level", "1600",
        ])
        assert result.eye_level == 1600.0
