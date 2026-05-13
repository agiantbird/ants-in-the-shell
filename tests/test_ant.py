"""Tests for Ant decision-making."""

import random

import pytest

from antfarm.actions import Dig, Idle, Move
from antfarm.ant import Ant
from antfarm.tile import Tile, TileKind
from antfarm.world import World


def _world_all_dirt(w: int = 5, h: int = 5) -> World:
    return World(width=w, height=h)


def _world_all_tunnel(w: int = 5, h: int = 5) -> World:
    world = World(width=w, height=h)
    for y in range(h):
        for x in range(w):
            world.set_tile(x, y, Tile(kind=TileKind.TUNNEL))
    return world


class TestMovementPreference:
    def test_moves_into_adjacent_tunnel(self):
        """When a tunnel is adjacent, the ant should Move rather than Dig."""
        world = _world_all_dirt()
        # carve a tunnel to the right of the ant
        world.dig(3, 2)

        found_move = False
        for seed in range(50):
            ant = Ant(x=2, y=2, rng=random.Random(seed))
            action = ant.step(world)
            if isinstance(action, Move) and action.x == 3 and action.y == 2:
                found_move = True
                break
        assert found_move, "Ant never chose to move into adjacent tunnel"


class TestDigging:
    def test_digs_when_surrounded_by_dirt(self):
        """All four neighbors are diggable dirt — the ant must Dig."""
        world = _world_all_dirt()
        ant = Ant(x=2, y=2, rng=random.Random(42))

        action = ant.step(world)

        assert isinstance(action, Dig)
        # The dug tile is exactly one step away, cardinally.
        assert abs(action.x - ant.x) + abs(action.y - ant.y) == 1


class TestIdle:
    def test_idles_when_boxed_in_by_edges(self):
        """A 1x1 world leaves the ant with no in-bounds neighbors."""
        world = World(width=1, height=1)
        # set ant in a tunnel
        world.set_tile(0, 0, Tile(kind=TileKind.TUNNEL))
        ant = Ant(x=0, y=0, rng=random.Random(0))

        action = ant.step(world)

        assert isinstance(action, Idle)


class TestRockAvoidance:
    def test_does_not_try_to_dig_rock(self):
        """An ant surrounded by rock should idle, not dig."""
        world = World(width=3, height=3)
        for y in range(3):
            for x in range(3):
                world.set_tile(x, y, Tile(kind=TileKind.ROCK))
        world.set_tile(1, 1, Tile(kind=TileKind.TUNNEL))

        ant = Ant(x=1, y=1, rng=random.Random(0))
        action = ant.step(world)
        assert isinstance(action, Idle)


class TestFoodPassability:
    def test_moves_into_adjacent_food(self):
        """Food is passable, ants step onto it like tunnel."""
        world = World(width=5, height=5)
        # Make the ant's tile and one neighbor passable.
        world.set_tile(2, 2, Tile(kind=TileKind.TUNNEL))
        world.set_tile(3, 2, Tile(kind=TileKind.FOOD, food_value=1))

        # Try a few seeds to find one where the ant picks the food
        # neighbor (others are dirt and would be Dig, not Move).
        found_move = False
        for seed in range(50):
            ant = Ant(x=2, y=2, rng=random.Random(seed))
            action = ant.step(world)
            if isinstance(action, Move) and action.x == 3 and action.y == 2:
                found_move = True
                break
        assert found_move, "Ant never chose to move onto food"


class TestDeterminism:
    def test_same_seed_same_action(self):
        """Two ants with the same seed in the same world decide identically."""
        world = _world_all_dirt()
        a1 = Ant(x=2, y=2, rng=random.Random(123))
        a2 = Ant(x=2, y=2, rng=random.Random(123))

        assert a1.step(world) == a2.step(world)

    @pytest.mark.parametrize("seed", [0, 1, 42, 999])
    def test_step_does_not_mutate_world_or_ant(self, seed):
        """Ant.step returns an Action but must not mutate anything."""
        world = _world_all_dirt()
        ant = Ant(x=2, y=2, rng=random.Random(seed))

        before_x, before_y, before_age = ant.x, ant.y, ant.age
        before_tile = world.tile_at(2, 2).kind

        ant.step(world)

        assert (ant.x, ant.y, ant.age) == (before_x, before_y, before_age)
        assert world.tile_at(2, 2).kind is before_tile
