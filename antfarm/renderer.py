"""A simple print-based terminal renderer."""

import os

from antfarm.simulation import Simulation
from antfarm.tile import TileKind

# Glyphs for each tile kind
_TILE_GLYPHS: dict[TileKind, str] = {
    TileKind.DIRT: "#",
    TileKind.TUNNEL: ".",
}

_ANT_GLYPH: str = "A"


class TerminalRenderer:
    """Renders a ``Simulation`` by reprinting its grid to stdout"""

    def render(self, simulation: Simulation) -> None:
        """Draw one frame."""
        self._clear()
        lines = self._frame_lines(simulation)
        print("\n".join(lines))

    def _frame_lines(self, simulation: Simulation) -> list[str]:
        """Build the frame as a list of strings, one per row."""
        world = simulation.world

        # Start from the tile grid, then overlay ants on top.
        rows: list[list[str]] = [
            [_TILE_GLYPHS[world.tile_at(x, y).kind] for x in range(world.width)]
            for y in range(world.height)
        ]
        for ant in simulation.colony:
            rows[ant.y][ant.x] = _ANT_GLYPH

        lines = ["".join(row) for row in rows]
        lines.append(f"tick {simulation.tick_count}  ants {len(simulation.colony)}")
        return lines

    @staticmethod
    def _clear() -> None:
        # nt is windows, cls clears window terminals. otherwise, use clear (mac/linux)
        os.system("cls" if os.name == "nt" else "clear")
