"""The ``World`` – the 2D grid of tiles and the rules about what's in it.

The grid is stored row-major (``grid[y][x]`` because that's how Python
list-of-lists naturally maps to a 2D display. But the *public* API uses
``(x, y)`` for motion, coordinates... everything, because that's how we think
about positions.
"""

from antfarm.exceptions import OutOfBoundsError, TileNotDiggableError
from antfarm.tile import Tile, TileKind


class World:
    """A 2D grid of tiles.

    Attributes:
        width: Number of columns.
        height: Number of rows.
    """

    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError(f"World dimensions must be positive, got {width} x {height}")
        self.width = width
        self.height = height

        # All dirt to start, ants dig their own tunnels.
        self._grid: list[list[Tile]] = [
            [Tile(kind=TileKind.DIRT) for _ in range(width)] for _ in range(height)
        ]

    # coordinate helpers
    def in_bounds(self, x: int, y: int) -> bool:
        """True if ``(x, y)`` is a valid coordinate."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _require_in_bounds(self, x: int, y: int) -> None:
        if not self.in_bounds(x, y):
            raise OutOfBoundsError(
                f"Coordinate ({x}, {y}) is outside the {self.width}x{self.height} world"
            )

    # reads

    def tile_at(self, x: int, y: int) -> Tile:
        """Return the tile at ``(x, y)``.

        Raises:
            OutOfBoundsError: if the coordinate is outside the grid
        """
        self._require_in_bounds(x, y)
        return self._grid[y][x]

    # mutations
    def dig(self, x: int, y: int) -> None:
        """Convert the tile at ``(x, y)`` to a tunnel.

        Raises:
            OutOfBounds Error: if the coordinate is outside the grid.
            TileNotDiggableError: if the tile cannot be dug.
        """
        tile = self.tile_at(x, y)
        if not tile.is_diggable():
            raise TileNotDiggableError(
                f"Tile at ({x}, {y}) is not diggable (kind={tile.kind.value})"
            )
        tile.kind = TileKind.TUNNEL

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        """Replace the tile at ``(x, y``.

        This is a low-level setter for world generation and tests.
        """
        self._require_in_bounds(x, y)
        self._grid[y][x] = tile
