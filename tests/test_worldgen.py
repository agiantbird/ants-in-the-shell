"""Tests for world generation."""

import random

import pytest

from antfarm import config, worldgen
from antfarm.tile import TileKind
from antfarm.world import World


def _fresh_world() -> World:
    return World(width=config.WORLD_WIDTH, height=config.WORLD_HEIGHT)


def _nest_xy(world: World) -> tuple[int, int]:
    return world.width // 2, world.height // 2


class TestDeterminism:
    def test_same_speed_produces_same_world(self):
        a, b = _fresh_world(), _fresh_world()
        nest = _nest_xy(a)

        worldgen.generate(a, random.Random(42), *nest)
        worldgen.generate(b, random.Random(42), *nest)

        for y in range(a.height):
            for x in range(a.width):
                assert a.tile_at(x, y).kind is b.tile_at(x, y).kind, f"Tiles differ at ({x}, {y})"

    def test_different_seeds_produce_different_worlds(self):
        a, b = _fresh_world(), _fresh_world()
        nest = _nest_xy(a)

        worldgen.generate(a, random.Random(1), *nest)
        worldgen.generate(b, random.Random(2), *nest)

        differences = sum(
            1
            for y in range(a.height)
            for x in range(a.width)
            if a.tile_at(x, y).kind is not b.tile_at(x, y).kind
        )
        assert differences > 0

    class TestNest:
        def test_nest_tile_is_set(self):
            world = _fresh_world()
            nx, ny = _nest_xy(world)

            worldgen.generate(world, random.Random(0), nx, ny)

            assert world.tile_at(nx, ny).kind is TileKind.NEST

        def test_nest_clearing_has_no_rocks_or_food(self):
            """Protected radius around nest should be free of rocks and food."""
            world = _fresh_world()
            nx, ny = _nest_xy(world)

            worldgen.generate(world, random.Random(0), nx, ny)

            for dy in range(-config.NEST_CLEAR_RADIUS, config.NEST_CLEAR_RADIUS + 1):
                for dx in range(-config.NEST_CLEAR_RADIUS, config.NEST_CLEAR_RADIUS + 1):
                    x, y = nx + dx, ny + dy
                    if not world.in_bounds(x, y):
                        continue
                    kind = world.tile_at(x, y).kind
                    assert kind not in (TileKind.ROCK, TileKind.FOOD), (
                        f"Found {kind} at ({x}, {y}), inside nest clearing"
                    )

        def test_immediate_neighbors_of_nest_are_tunnels(self):
            """Ants need somewhere to step on tick 1."""
            world = _fresh_world()
            nx, ny = _nest_xy(world)

            worldgen.generate(world, random.Random(0), nx, ny)

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                x, y = nx + dx, ny + dy
                if not world.in_bounds(x, y):
                    continue
                assert world.tile_at(x, y).kind is TileKind.TUNNEL


class TestDensity:
    """Check rocks/food appear in allowable amounts."""

    def test_rocks_appear(self):
        rock_counts = []
        for seed in range(5):
            world = _fresh_world()
            worldgen.generate(world, random.Random(seed), *_nest_xy(world))
            rock_counts.append(_count(world, TileKind.ROCK))

        # Every seed should produce some rocks.
        assert all(c > 0 for c in rock_counts), f"Seed produced zero rocks: {rock_counts}"

    def test_food_appears(self):
        food_counts = []
        for seed in range(5):
            world = _fresh_world()
            worldgen.generate(world, random.Random(seed), *_nest_xy(world))
            food_counts.append(_count(world, TileKind.FOOD))

        # Every seed should produce some food.
        assert all(c > 0 for c in food_counts), f"Seed produced zero food: {food_counts}"


class TestEdgeCases:
    def test_tiny_world_does_not_crash(self):
        """A 5×5 world with the nest in the middle has very little room
        for obstacles. Generation should still complete without
        raising."""
        world = World(width=5, height=5)
        nx, ny = 2, 2

        worldgen.generate(world, random.Random(0), nx, ny)

        assert world.tile_at(nx, ny).kind is TileKind.NEST

    @pytest.mark.parametrize("seed", range(10))
    def test_no_rocks_inside_nest_clearing_across_seeds(self, seed):
        """The nest clearing rule should hold regardless of seed."""
        world = _fresh_world()
        nx, ny = _nest_xy(world)

        worldgen.generate(world, random.Random(seed), nx, ny)

        for dy in range(-config.NEST_CLEAR_RADIUS, config.NEST_CLEAR_RADIUS + 1):
            for dx in range(-config.NEST_CLEAR_RADIUS, config.NEST_CLEAR_RADIUS + 1):
                x, y = nx + dx, ny + dy
                if not world.in_bounds(x, y):
                    continue
                assert world.tile_at(x, y).kind is not TileKind.ROCK


def _count(world: World, kind: TileKind) -> int:
    return sum(
        1
        for y in range(world.height)
        for x in range(world.width)
        if world.tile_at(x, y).kind is kind
    )
