"""Tests for the World class."""

import pytest

from antfarm.exceptions import OutOfBoundsError, TileNotDiggableError
from antfarm.tile import TileKind
from antfarm.world import World


class TestConstruction:
    def test_world_starts_all_dirt(self):
        world = World(width=3, height=2)
        for y in range(2):
            for x in range(3):
                assert world.tile_at(x, y).kind is TileKind.DIRT

    def test_world_dimensions(self):
        world = World(width=5, height=7)
        assert world.width == 5
        assert world.height == 7

    @pytest.mark.parametrize(
        ("width", "height"),
        [(0,5), (5,0), (-1, 5), (5, -1), (0, 0)],
    )
    def test_nonpositive_dimensions_rejected(self, width, height):
        with pytest.raises(ValueError, match="positive"):
            World(width=width, height=height)


class TestBounds:
    def test_in_bounds_corners(self):
        world = World(width=3, height=2)
        assert world.in_bounds(0, 0)
        assert world.in_bounds(2, 1)

    def test_out_of_bounds(self):
        world = World(width=3, height=2)
        assert not world.in_bounds(-1, 0)
        assert not world.in_bounds(0, -1)
        assert not world.in_bounds(3, 0)
        assert not world.in_bounds(0, 2)

    def test_tile_at_rejects_out_of_bounds(self):
        world = World(width=3, height=2)
        with pytest.raises(OutOfBoundsError):
            world.tile_at(5, 5)


class TestDigging:
    def test_dig_converts_dirt_to_tunnel(self):
        world = World(width=3, height=3)
        tile = world.tile_at(1, 1)
        assert tile.kind is TileKind.DIRT
        world.dig(1, 1)
        assert tile.kind is TileKind.TUNNEL

    def test_dig_raises_on_non_diggable_tile(self):
        world = World(width=3, height=3)
        world.dig(1, 1) # tile is now a tunnel
        with pytest.raises(TileNotDiggableError):
            world.dig(1, 1)

    def test_dig_raises_out_of_bounds(self):
        world = World(width=3, height=3)
        with pytest.raises(OutOfBoundsError):
            world.dig(-1, 0)

