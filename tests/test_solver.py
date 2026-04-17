import pytest

from gallery_wall_organiser.geometry import (
    edge_distance,
    is_within_bounds,
    overlaps_obstacle,
    placements_overlap,
)
from gallery_wall_organiser.models import Layout, Obstacle, Photo, Placement, Wall
from gallery_wall_organiser.solver import initialize_grid


class TestInitializeGridReturnsLayout:
    def test_returns_layout(self):
        wall = Wall(height=400, width=600)
        photos = [Photo(height=50, width=50)]

        result = initialize_grid(wall, photos, [], 200)

        assert isinstance(result, Layout)

    def test_layout_has_correct_wall(self):
        wall = Wall(height=400, width=600)
        photos = [Photo(height=50, width=50)]

        result = initialize_grid(wall, photos, [], 200)

        assert result.wall is wall

    def test_layout_has_correct_eye_level(self):
        wall = Wall(height=400, width=600)
        photos = [Photo(height=50, width=50)]

        result = initialize_grid(wall, photos, [], 200)

        assert result.eye_level == 200

    def test_layout_has_correct_obstacles(self):
        wall = Wall(height=400, width=600)
        photos = [Photo(height=50, width=50)]
        obstacles = [Obstacle(x=300, y=200, height=30, width=30)]

        result = initialize_grid(wall, photos, obstacles, 200)

        assert result.obstacles == obstacles

    def test_placement_count_matches_photos(self):
        wall = Wall(height=400, width=600)
        photos = [
            Photo(height=50, width=50),
            Photo(height=60, width=40),
            Photo(height=70, width=80),
        ]

        result = initialize_grid(wall, photos, [], 200)

        assert len(result.placements) == 3

    def test_each_placement_uses_correct_photo(self):
        wall = Wall(height=400, width=600)
        photos = [
            Photo(height=50, width=50),
            Photo(height=60, width=40),
        ]

        result = initialize_grid(wall, photos, [], 200)

        placed_photos = sorted(
            [(p.photo.height, p.photo.width) for p in result.placements]
        )
        expected = sorted([(p.height, p.width) for p in photos])
        assert placed_photos == expected


class TestInitializeGridWithinBounds:
    def test_all_placements_within_bounds(self):
        wall = Wall(height=400, width=600)
        photos = [
            Photo(height=50, width=50),
            Photo(height=60, width=40),
            Photo(height=70, width=80),
        ]

        result = initialize_grid(wall, photos, [], 200)

        for p in result.placements:
            assert is_within_bounds(p, wall), f"Placement at ({p.x}, {p.y}) out of bounds"

    def test_single_large_photo_within_bounds(self):
        wall = Wall(height=400, width=600)
        photos = [Photo(height=300, width=500)]

        result = initialize_grid(wall, photos, [], 200)

        assert is_within_bounds(result.placements[0], wall)

    def test_many_small_photos_within_bounds(self):
        wall = Wall(height=800, width=800)
        photos = [Photo(height=30, width=30) for _ in range(9)]

        result = initialize_grid(wall, photos, [], 400)

        for p in result.placements:
            assert is_within_bounds(p, wall)


class TestInitializeGridNoObstacleOverlaps:
    def test_no_placement_overlaps_obstacle(self):
        wall = Wall(height=400, width=600)
        photos = [
            Photo(height=50, width=50),
            Photo(height=50, width=50),
        ]
        obstacles = [Obstacle(x=200, y=150, height=100, width=100)]

        result = initialize_grid(wall, photos, obstacles, 200)

        for p in result.placements:
            for obs in obstacles:
                assert not overlaps_obstacle(p, obs), (
                    f"Placement at ({p.x}, {p.y}) overlaps obstacle at ({obs.x}, {obs.y})"
                )

    def test_multiple_obstacles(self):
        wall = Wall(height=600, width=600)
        photos = [
            Photo(height=50, width=50),
            Photo(height=50, width=50),
            Photo(height=50, width=50),
        ]
        obstacles = [
            Obstacle(x=100, y=100, height=80, width=80),
            Obstacle(x=300, y=300, height=80, width=80),
        ]

        result = initialize_grid(wall, photos, obstacles, 300)

        for p in result.placements:
            for obs in obstacles:
                assert not overlaps_obstacle(p, obs)


class TestInitializeGridNoPhotoOverlaps:
    def test_no_placements_overlap_each_other(self):
        wall = Wall(height=400, width=600)
        photos = [
            Photo(height=50, width=50),
            Photo(height=60, width=40),
            Photo(height=70, width=80),
        ]

        result = initialize_grid(wall, photos, [], 200)

        placements = result.placements
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                assert not placements_overlap(placements[i], placements[j]), (
                    f"Placements {i} and {j} overlap"
                )

    def test_many_photos_no_overlaps(self):
        wall = Wall(height=800, width=800)
        photos = [Photo(height=40, width=40) for _ in range(6)]

        result = initialize_grid(wall, photos, [], 400)

        placements = result.placements
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                assert not placements_overlap(placements[i], placements[j])


class TestInitializeGridGapUniformity:
    def test_gaps_approximately_uniform(self):
        # With equal-sized photos on a large wall, gaps should be roughly equal
        wall = Wall(height=400, width=600)
        photos = [Photo(height=50, width=50) for _ in range(4)]

        result = initialize_grid(wall, photos, [], 200)

        placements = result.placements
        # Compute pairwise edge distances for adjacent photos
        distances = []
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                d = edge_distance(placements[i], placements[j])
                if d > 0:
                    distances.append(d)
        if len(distances) >= 2:
            mean = sum(distances) / len(distances)
            max_deviation = max(abs(d - mean) for d in distances)
            # Gaps shouldn't vary by more than 3x the mean
            assert max_deviation < 3 * mean


class TestInitializeGridSinglePhoto:
    def test_single_photo_placed_within_bounds(self):
        wall = Wall(height=200, width=200)
        photos = [Photo(height=50, width=50)]

        result = initialize_grid(wall, photos, [], 100)

        assert len(result.placements) == 1
        assert is_within_bounds(result.placements[0], wall)

    def test_single_photo_no_obstacle_overlap(self):
        wall = Wall(height=200, width=200)
        photos = [Photo(height=50, width=50)]
        obstacles = [Obstacle(x=75, y=75, height=50, width=50)]

        result = initialize_grid(wall, photos, obstacles, 100)

        assert not overlaps_obstacle(result.placements[0], obstacles[0])


class TestInitializeGridMixedSizes:
    def test_different_sized_photos(self):
        wall = Wall(height=600, width=800)
        photos = [
            Photo(height=100, width=150),
            Photo(height=50, width=50),
            Photo(height=80, width=120),
        ]

        result = initialize_grid(wall, photos, [], 300)

        assert len(result.placements) == 3
        for p in result.placements:
            assert is_within_bounds(p, wall)
        placements = result.placements
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                assert not placements_overlap(placements[i], placements[j])
