import math
import random

import pytest

from gallery_wall_organiser.geometry import (
    edge_distance,
    is_within_bounds,
    overlaps_obstacle,
    placements_overlap,
)
from gallery_wall_organiser.models import Layout, Obstacle, Photo, Placement, Wall
from gallery_wall_organiser.solver import (
    accept,
    initialize_grid,
    perturb_position,
    swap_placements,
)


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


def _make_layout():
    """Helper: 3-photo layout for perturbation/swap tests."""
    wall = Wall(height=400, width=600)
    return Layout(
        wall=wall,
        placements=[
            Placement(photo=Photo(height=50, width=50), x=100, y=100),
            Placement(photo=Photo(height=60, width=40), x=300, y=100),
            Placement(photo=Photo(height=70, width=80), x=200, y=250),
        ],
        obstacles=[],
        d=0,
        eye_level=200,
    )


class TestPerturbPositionReturnsLayout:
    def test_returns_layout(self):
        layout = _make_layout()

        result = perturb_position(layout, 0, 10.0)

        assert isinstance(result, Layout)

    def test_same_number_of_placements(self):
        layout = _make_layout()

        result = perturb_position(layout, 1, 10.0)

        assert len(result.placements) == len(layout.placements)

    def test_wall_unchanged(self):
        layout = _make_layout()

        result = perturb_position(layout, 0, 10.0)

        assert result.wall is layout.wall

    def test_obstacles_unchanged(self):
        layout = _make_layout()

        result = perturb_position(layout, 0, 10.0)

        assert result.obstacles is layout.obstacles

    def test_eye_level_unchanged(self):
        layout = _make_layout()

        result = perturb_position(layout, 0, 10.0)

        assert result.eye_level == layout.eye_level


class TestPerturbPositionTargetOnly:
    def test_other_placements_unchanged(self):
        layout = _make_layout()

        result = perturb_position(layout, 1, 10.0)

        # Index 0 and 2 should be identical
        assert result.placements[0].x == layout.placements[0].x
        assert result.placements[0].y == layout.placements[0].y
        assert result.placements[0].photo is layout.placements[0].photo
        assert result.placements[2].x == layout.placements[2].x
        assert result.placements[2].y == layout.placements[2].y
        assert result.placements[2].photo is layout.placements[2].photo

    def test_targeted_photo_same(self):
        layout = _make_layout()

        result = perturb_position(layout, 0, 10.0)

        assert result.placements[0].photo is layout.placements[0].photo


class TestPerturbPositionShiftBounded:
    def test_shift_within_max_delta(self):
        layout = _make_layout()
        max_delta = 15.0

        result = perturb_position(layout, 0, max_delta)

        dx = abs(result.placements[0].x - layout.placements[0].x)
        dy = abs(result.placements[0].y - layout.placements[0].y)
        assert dx <= max_delta
        assert dy <= max_delta

    def test_zero_delta_no_change(self):
        layout = _make_layout()

        result = perturb_position(layout, 0, 0.0)

        assert result.placements[0].x == layout.placements[0].x
        assert result.placements[0].y == layout.placements[0].y

    def test_repeated_perturbations_all_bounded(self):
        layout = _make_layout()
        max_delta = 5.0

        for _ in range(20):
            result = perturb_position(layout, 0, max_delta)
            dx = abs(result.placements[0].x - layout.placements[0].x)
            dy = abs(result.placements[0].y - layout.placements[0].y)
            assert dx <= max_delta
            assert dy <= max_delta


class TestPerturbPositionDoesNotMutate:
    def test_original_layout_unchanged(self):
        layout = _make_layout()
        orig_x = layout.placements[0].x
        orig_y = layout.placements[0].y

        perturb_position(layout, 0, 10.0)

        assert layout.placements[0].x == orig_x
        assert layout.placements[0].y == orig_y


class TestSwapPlacementsReturnsLayout:
    def test_returns_layout(self):
        layout = _make_layout()

        result = swap_placements(layout, 0, 2)

        assert isinstance(result, Layout)

    def test_same_number_of_placements(self):
        layout = _make_layout()

        result = swap_placements(layout, 0, 1)

        assert len(result.placements) == len(layout.placements)

    def test_wall_unchanged(self):
        layout = _make_layout()

        result = swap_placements(layout, 0, 1)

        assert result.wall is layout.wall


class TestSwapPlacementsPositions:
    def test_positions_swapped(self):
        layout = _make_layout()

        result = swap_placements(layout, 0, 2)

        # Photo 0 should now be at photo 2's old position
        assert result.placements[0].x == layout.placements[2].x
        assert result.placements[0].y == layout.placements[2].y
        # Photo 2 should now be at photo 0's old position
        assert result.placements[2].x == layout.placements[0].x
        assert result.placements[2].y == layout.placements[0].y

    def test_photos_swapped(self):
        layout = _make_layout()

        result = swap_placements(layout, 0, 1)

        assert result.placements[0].photo is layout.placements[1].photo
        assert result.placements[1].photo is layout.placements[0].photo

    def test_other_placement_unchanged(self):
        layout = _make_layout()

        result = swap_placements(layout, 0, 1)

        assert result.placements[2].x == layout.placements[2].x
        assert result.placements[2].y == layout.placements[2].y
        assert result.placements[2].photo is layout.placements[2].photo


class TestSwapPlacementsSameIndex:
    def test_swap_same_index_no_change(self):
        layout = _make_layout()

        result = swap_placements(layout, 1, 1)

        for k in range(len(layout.placements)):
            assert result.placements[k].x == layout.placements[k].x
            assert result.placements[k].y == layout.placements[k].y
            assert result.placements[k].photo is layout.placements[k].photo


class TestSwapPlacementsDoesNotMutate:
    def test_original_layout_unchanged(self):
        layout = _make_layout()
        orig_photos = [p.photo for p in layout.placements]
        orig_positions = [(p.x, p.y) for p in layout.placements]

        swap_placements(layout, 0, 2)

        for k in range(len(layout.placements)):
            assert layout.placements[k].photo is orig_photos[k]
            assert (layout.placements[k].x, layout.placements[k].y) == orig_positions[k]


class TestAcceptImprovement:
    def test_negative_delta_cost_always_true(self):
        """Improvement (negative delta_cost) should always be accepted."""
        for delta in [-1.0, -10.0, -100.0]:
            for temp in [1.0, 10.0, 100.0, 1000.0]:
                result = accept(delta, temp)
                assert result is True, f"delta_cost={delta}, temperature={temp}"


class TestAcceptNoChange:
    def test_zero_delta_cost_always_true(self):
        """Zero cost delta (no improvement, no worse) should always be accepted."""
        for temp in [0.0, 1.0, 10.0, 100.0]:
            result = accept(0.0, temp)
            assert result is True


class TestAcceptZeroTemperature:
    def test_worse_cost_zero_temp_false(self):
        """With zero temperature, worse cost should always be rejected."""
        for delta in [0.1, 1.0, 10.0, 100.0]:
            result = accept(delta, 0.0)
            assert result is False, f"delta_cost={delta}, temperature=0.0"

    def test_zero_delta_zero_temp_true(self):
        """Zero cost delta with zero temperature should be accepted."""
        result = accept(0.0, 0.0)
        assert result is True

    def test_improvement_zero_temp_true(self):
        """Improvement with zero temperature should be accepted."""
        result = accept(-5.0, 0.0)
        assert result is True


class TestAcceptHighTemperature:
    def test_high_temp_high_probability_worse(self):
        """High temperature should lead to high acceptance probability for worse cost."""
        random.seed(42)
        accepts = sum(accept(50.0, 1000.0) for _ in range(100))
        # With very high temp, should accept almost always (prob ≈ exp(-50/1000) ≈ 0.95)
        assert accepts >= 90, f"Expected high acceptance rate, got {accepts}/100"

    def test_very_high_temp_worse_acceptance(self):
        """Very high temperature should approach random walk (almost always accept)."""
        random.seed(123)
        accepts = sum(accept(100.0, 10000.0) for _ in range(100))
        # exp(-100/10000) ≈ 0.99, so almost always accept
        assert accepts >= 95

    def test_moderate_temp_some_rejection(self):
        """Moderate temperature with large penalty should have some rejection."""
        random.seed(99)
        accepts = sum(accept(100.0, 10.0) for _ in range(100))
        # exp(-100/10) ≈ 3.7e-5, should reject almost always
        assert accepts <= 5, f"Expected few accepts, got {accepts}/100"


class TestAcceptProbabilistic:
    def test_metropolis_criterion_accepts_with_expected_probability(self):
        """Verify acceptance follows exp(-delta_cost / temperature) approximately."""
        random.seed(12345)
        delta_cost = 20.0
        temperature = 10.0
        expected_prob = math.exp(-delta_cost / temperature)
        # Run 1000 trials
        accepts = sum(accept(delta_cost, temperature) for _ in range(1000))
        observed_prob = accepts / 1000.0
        # Check observed is within reasonable range of expected (±5% tolerance)
        assert abs(observed_prob - expected_prob) < 0.05, (
            f"Expected ~{expected_prob:.3f}, got {observed_prob:.3f}"
        )

    def test_small_delta_small_temp_high_prob(self):
        """Small delta with small temperature should have moderate acceptance."""
        random.seed(456)
        # exp(-5/5) = exp(-1) ≈ 0.368
        accepts = sum(accept(5.0, 5.0) for _ in range(1000))
        prob = accepts / 1000.0
        assert 0.3 < prob < 0.45

    def test_large_delta_small_temp_low_prob(self):
        """Large delta with small temperature should have low acceptance."""
        random.seed(789)
        # exp(-50/1) = exp(-50) ≈ 1.9e-22
        accepts = sum(accept(50.0, 1.0) for _ in range(1000))
        prob = accepts / 1000.0
        assert prob < 0.01

    def test_small_delta_large_temp_high_prob(self):
        """Small delta with large temperature should have high acceptance."""
        random.seed(321)
        # exp(-5/100) ≈ 0.951
        accepts = sum(accept(5.0, 100.0) for _ in range(1000))
        prob = accepts / 1000.0
        assert prob > 0.90


class TestAcceptEdgeCases:
    def test_very_small_positive_delta(self):
        """Very small positive delta should have high acceptance at high temp."""
        random.seed(111)
        # exp(-0.01/100) ≈ 0.9999
        accepts = sum(accept(0.01, 100.0) for _ in range(100))
        assert accepts >= 99

    def test_deterministic_sequence_with_seed(self):
        """Fixed seed should produce deterministic results."""
        results1 = [accept(10.0, 5.0) for _ in range(10)]
        random.seed(555)
        results2 = [accept(10.0, 5.0) for _ in range(10)]
        random.seed(555)
        results3 = [accept(10.0, 5.0) for _ in range(10)]
        assert results2 == results3
