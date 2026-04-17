import pytest

from gallery_wall_organiser.models import Obstacle, Photo, Wall


class TestWall:
    def test_stores_height_and_width(self):
        wall = Wall(height=2400, width=1800)

        assert wall.height == 2400
        assert wall.width == 1800

    def test_zero_height_raises(self):
        with pytest.raises(ValueError):
            Wall(height=0, width=1800)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError):
            Wall(height=-1, width=1800)

    def test_zero_width_raises(self):
        with pytest.raises(ValueError):
            Wall(height=2400, width=0)

    def test_negative_width_raises(self):
        with pytest.raises(ValueError):
            Wall(height=2400, width=-1)


class TestPhoto:
    def test_stores_height_and_width(self):
        photo = Photo(height=400, width=300)

        assert photo.height == 400
        assert photo.width == 300

    def test_zero_height_raises(self):
        with pytest.raises(ValueError):
            Photo(height=0, width=300)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError):
            Photo(height=-10, width=300)

    def test_zero_width_raises(self):
        with pytest.raises(ValueError):
            Photo(height=400, width=0)

    def test_negative_width_raises(self):
        with pytest.raises(ValueError):
            Photo(height=400, width=-5)


class TestObstacle:
    def test_stores_all_attributes(self):
        obstacle = Obstacle(x=100, y=900, height=80, width=120)

        assert obstacle.x == 100
        assert obstacle.y == 900
        assert obstacle.height == 80
        assert obstacle.width == 120

    def test_zero_height_raises(self):
        with pytest.raises(ValueError):
            Obstacle(x=100, y=900, height=0, width=120)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError):
            Obstacle(x=100, y=900, height=-1, width=120)

    def test_zero_width_raises(self):
        with pytest.raises(ValueError):
            Obstacle(x=100, y=900, height=80, width=0)

    def test_negative_width_raises(self):
        with pytest.raises(ValueError):
            Obstacle(x=100, y=900, height=80, width=-5)

    def test_x_and_y_can_be_zero_or_negative(self):
        # Position coordinates are not constrained to be positive
        obstacle = Obstacle(x=0, y=-10, height=80, width=120)

        assert obstacle.x == 0
        assert obstacle.y == -10
