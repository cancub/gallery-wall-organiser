import pytest

from gallery_wall_organiser.models import Layout, Obstacle, Photo, Placement, Wall


@pytest.mark.parametrize("factory", [
    lambda h, w: Wall(height=h, width=w),
    lambda h, w: Photo(height=h, width=w),
    lambda h, w: Obstacle(x=0, y=0, height=h, width=w),
])
class TestDimensionValidation:
    def test_zero_height_raises(self, factory):
        with pytest.raises(ValueError):
            factory(0, 100)

    def test_negative_height_raises(self, factory):
        with pytest.raises(ValueError):
            factory(-1, 100)

    def test_zero_width_raises(self, factory):
        with pytest.raises(ValueError):
            factory(100, 0)

    def test_negative_width_raises(self, factory):
        with pytest.raises(ValueError):
            factory(100, -1)


class TestWall:
    def test_stores_height_and_width(self):
        wall = Wall(height=2400, width=1800)

        assert wall.height == 2400
        assert wall.width == 1800


class TestPhoto:
    def test_stores_height_and_width(self):
        photo = Photo(height=400, width=300)

        assert photo.height == 400
        assert photo.width == 300


class TestObstacle:
    def test_stores_all_attributes(self):
        obstacle = Obstacle(x=100, y=900, height=80, width=120)

        assert obstacle.x == 100
        assert obstacle.y == 900
        assert obstacle.height == 80
        assert obstacle.width == 120

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


@pytest.fixture
def simple_layout():
    wall = Wall(height=2400, width=1800)
    photo = Photo(height=400, width=300)
    placements = [Placement(photo=photo, x=100, y=200)]
    obstacles = [Obstacle(x=50, y=100, height=80, width=60)]
    return Layout(wall=wall, placements=placements, obstacles=obstacles, d=20, eye_level=1450)


class TestLayout:
    def test_stores_all_attributes(self, simple_layout):
        wall = Wall(height=2400, width=1800)
        photo = Photo(height=400, width=300)
        placements = [Placement(photo=photo, x=100, y=200)]
        obstacles = [Obstacle(x=50, y=100, height=80, width=60)]
        layout = Layout(wall=wall, placements=placements, obstacles=obstacles, d=20, eye_level=1450)

        assert layout.wall is wall
        assert layout.placements is placements
        assert layout.obstacles is obstacles
        assert layout.d == 20
        assert layout.eye_level == 1450

    def test_horizontal_center_is_half_wall_width(self, simple_layout):
        assert simple_layout.horizontal_center == 900  # 1800 / 2

    def test_vertical_split_equals_eye_level(self, simple_layout):
        assert simple_layout.vertical_split == 1450

    def test_horizontal_center_reflects_wall_width(self):
        wall = Wall(height=2400, width=1000)
        layout = Layout(wall=wall, placements=[], obstacles=[], d=20, eye_level=1450)

        assert layout.horizontal_center == 500  # 1000 / 2

    def test_vertical_split_reflects_eye_level(self):
        wall = Wall(height=2400, width=1800)
        layout = Layout(wall=wall, placements=[], obstacles=[], d=20, eye_level=1200)

        assert layout.vertical_split == 1200

    def test_empty_placements_and_obstacles_are_accepted(self):
        wall = Wall(height=2400, width=1800)
        layout = Layout(wall=wall, placements=[], obstacles=[], d=10, eye_level=1450)

        assert layout.placements == []
        assert layout.obstacles == []

    def test_multiple_placements_are_stored(self):
        wall = Wall(height=2400, width=1800)
        photo = Photo(height=400, width=300)
        placements = [
            Placement(photo=photo, x=0, y=0),
            Placement(photo=photo, x=400, y=0),
        ]
        layout = Layout(wall=wall, placements=placements, obstacles=[], d=20, eye_level=1450)

        assert len(layout.placements) == 2

