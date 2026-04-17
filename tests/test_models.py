import pytest

from gallery_wall_organiser.models import Obstacle, Photo, Placement, Wall


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


class TestPlacement:
    def test_stores_photo_and_position(self):
        photo = Photo(height=400, width=300)
        placement = Placement(photo=photo, x=100, y=200)

        assert placement.photo is photo
        assert placement.x == 100
        assert placement.y == 200

    def test_left_equals_x(self):
        photo = Photo(height=400, width=300)
        placement = Placement(photo=photo, x=150, y=200)

        assert placement.left == 150

    def test_top_equals_y(self):
        photo = Photo(height=400, width=300)
        placement = Placement(photo=photo, x=150, y=200)

        assert placement.top == 200

    def test_right_equals_x_plus_photo_width(self):
        photo = Photo(height=400, width=300)
        placement = Placement(photo=photo, x=150, y=200)

        assert placement.right == 450  # 150 + 300

    def test_bottom_equals_y_plus_photo_height(self):
        photo = Photo(height=400, width=300)
        placement = Placement(photo=photo, x=150, y=200)

        assert placement.bottom == 600  # 200 + 400

    def test_edges_at_origin(self):
        photo = Photo(height=100, width=200)
        placement = Placement(photo=photo, x=0, y=0)

        assert placement.left == 0
        assert placement.top == 0
        assert placement.right == 200
        assert placement.bottom == 100

    def test_x_and_y_can_be_negative(self):
        photo = Photo(height=100, width=200)
        placement = Placement(photo=photo, x=-50, y=-25)

        assert placement.left == -50
        assert placement.top == -25
        assert placement.right == 150   # -50 + 200
        assert placement.bottom == 75  # -25 + 100

