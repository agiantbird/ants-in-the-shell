"""Tests for the Tile dataclass."""

from antfarm.tile import Tile, TileKind


def test_dirt_is_diggable():
    tile = Tile(kind=TileKind.DIRT)
    assert tile.is_diggable()
    assert not tile.is_passable()


def test_tunnel_is_passable_not_diggable():
    tile = Tile(kind=TileKind.TUNNEL)
    assert tile.is_passable()
    assert not tile.is_diggable()
