"""Tiles: the cells that make up the world grid.

A ``Tile`` carries both its ``TileKind`` (what it is) and any per-tile
state that future features will need (hardness, food value, pheromone
level).
"""

from dataclasses import dataclass
from enum import Enum


class TileKind(Enum):
    """What kind of thing occupies a tile."""

    DIRT = "dirt"
    TUNNEL = "tunnel"
    ROCK = "rock"
    FOOD = "food"
    NEST = "nest"



@dataclass
class Tile:
    """A single cell in the world grid.

    Attributes:
        kind: What kind of tile is this
        food_value: How much food this tile holds, 0 for non-food tiles.
    """

    kind: TileKind
    food_value: int = 0


    def is_diggable(self) -> bool:
        """Can an ant dig through this tile?

        Only dirt is diggable.
        """
        return self.kind is TileKind.DIRT

    def is_passable(self) -> bool:
        """Can an ant move onto this tile without digging?

        Tunnels and the nest are passable as is food, as food is consumed and becomes tunnel.
        """
        return self.kind in (TileKind.TUNNEL, TileKind.NEST, TileKind.FOOD)

    def is_food(self) -> bool:
        """Is there food on this tile that an ant could eat?"""
        return self.kind is TileKind.FOOD and self.food_value > 0

    def is_nest(self) -> bool:
        """Is this the colony's nest tile?"""
        return self.kind is TileKind.NEST
