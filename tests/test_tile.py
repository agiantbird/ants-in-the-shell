"""Tests for the Tile dataclass."""

from antfarm.tile import Tile, TileKind


class TestDirt:
    def test_dirt_is_diggable(self):
        tile = Tile(kind=TileKind.DIRT)
        assert tile.is_diggable()

    def test_dirt_is_not_passable(self):
        assert not Tile(kind=TileKind.DIRT).is_passable()


class TestTunnel:
    def test_tunnel_is_passable(self):
        assert Tile(kind=TileKind.TUNNEL).is_passable()

    def test_tunnel_is_not_diggable(self):
        assert not Tile(kind=TileKind.TUNNEL).is_diggable()


class TestRock:
    def test_rock_is_not_diggable(self):
        assert not Tile(kind=TileKind.ROCK).is_diggable()

    def test_rock_is_not_passable(self):
        assert not Tile(kind=TileKind.ROCK).is_passable()


class TestFood:
    def test_food_is_passable(self):
        """Ants step onto food and eat it in the same motion."""
        tile = Tile(kind=TileKind.FOOD, food_value=1)
        assert tile.is_passable()

    def test_food_is_not_diggable(self):
        tile = Tile(kind=TileKind.FOOD, food_value=1)
        assert not tile.is_diggable()

    def test_food_with_value_reports_food(self):
        tile = Tile(kind=TileKind.FOOD, food_value=1)
        assert tile.is_food()

    def test_food_with_zero_value_is_not_food(self):
        """A food tile with zero value shouldn't be edible."""
        tile = Tile(kind=TileKind.FOOD, food_value=0)
        assert not tile.is_food()


class TestNest:
    def test_nest_is_passable(self):
        assert Tile(kind=TileKind.NEST).is_passable()

    def test_nest_is_not_diggable(self):
        assert not Tile(kind=TileKind.NEST).is_diggable()

    def test_nest_reports_nest(self):
        assert Tile(kind=TileKind.NEST).is_nest()

    def test_other_kinds_are_not_nest(self):
        for kind in (TileKind.DIRT, TileKind.TUNNEL, TileKind.ROCK, TileKind.FOOD):
            assert not Tile(kind=kind).is_nest()


def test_default_food_value_is_zero():
    """Non-food tiles shouldn't need to specify food_value."""
    assert Tile(kind=TileKind.DIRT).food_value == 0
