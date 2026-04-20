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


@dataclass
class Tile:
    """A single cell in the world grid."""

    kind: TileKind

    def is_diggable(self) -> bool:
        """Can an ant dig through this tile?"""
        return self.kind is TileKind.DIRT


    def is_passable(self) -> bool:
        """Can an ant move onto this tile without digging?"""
        return self.kind is TileKind.TUNNEL
