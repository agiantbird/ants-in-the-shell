"""Renderers: read a ``Simulation`` and produce output.

There are two renderers:

- ``StringRenderer`` produces a list of strings describing the current frame.
    Used for tests and by ``CursesRenderer under the hood.

- ``CursesRenderer`` uses the ``curses`` module to paint the frame into a
    terminal window without flickering, adds color when supported by the
    terminal and falls back to monochrome
"""
import curses
from contextlib import suppress

from antfarm.simulation import Simulation
from antfarm.tile import TileKind

# Glyphs for each tile kind
_TILE_GLYPHS: dict[TileKind, str] = {
    TileKind.DIRT: "#",
    TileKind.TUNNEL: ".",
    TileKind.ROCK: "R",
    TileKind.FOOD: "F",
    TileKind.NEST: "@"
}

_ANT_GLYPH: str = "A"


class StringRenderer:
    """Renders a simulation as a list of strings."""

    def frame_lines(self, simulation: Simulation) -> list[str]:
        """Return one string per row, plus a status line at the end."""
        world = simulation.world

        rows: list[list[str]] = [
            [_TILE_GLYPHS[world.tile_at(x, y).kind] for x in range(world.width)]
            for y in range(world.height)
        ]
        for ant in simulation.colony:
            rows[ant.y][ant.x] = _ANT_GLYPH

        lines = ["".join(row) for row in rows]
        lines.append(self._status_line(simulation))
        return lines

    @staticmethod
    def _status_line(simulation: Simulation) -> str:
        state = "PAUSED" if simulation.is_paused else "running"
        return (
            f"tick {simulation.tick_count}  "
            f"ants {len(simulation.colony)}  "
            f"food {simulation.food_remaining}  "
            f"reserves {simulation.colony.food_reserves}  "
            f"speed {simulation.speed:g}x  "
            f"[{state}]  "
            f"(q quit, p pause, +/- speed)"
        )

# -- Curses renderer ---------------------------------------------------

# Color pair IDs. Curses requires you to pre-declare (fg, bg) pairs as
# numbered slots, then refer to them by number when drawing.


_COLOR_DIRT = 1
_COLOR_TUNNEL = 2
_COLOR_ANT = 3
_COLOR_STATUS = 4
_COLOR_ROCK = 5
_COLOR_FOOD = 6
_COLOR_NEST = 7


class CursesRenderer:
    """Renders a simulation to a curses window.

    Must be constructed with an initialized curses window (obtained via ``curses.wrapper``)
    """
    def __init__(self, window: "curses.window") -> None:
        self._window = window
        self._string_renderer = StringRenderer()
        self._color_enabled = self._init_colors()

        # hide the blinking cursor, not all terminals
        # support hiding the cursor, so failures are
        # suppressed
        with suppress(curses.error):
            curses.curs_set(0)

    @staticmethod
    def _init_colors() -> bool:
        """Set up color pairs if the terminal supports it"""
        if not curses.has_colors():
            return False

        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1  # a terminal's default background
        except curses.error:
            bg = curses.COLOR_BLACK

        curses.init_pair(_COLOR_DIRT, curses.COLOR_YELLOW, bg)
        curses.init_pair(_COLOR_TUNNEL, curses.COLOR_WHITE, bg)
        curses.init_pair(_COLOR_ANT, curses.COLOR_RED, bg)
        curses.init_pair(_COLOR_STATUS, curses.COLOR_CYAN, bg)
        curses.init_pair(_COLOR_ROCK, curses.COLOR_BLUE, bg)
        curses.init_pair(_COLOR_FOOD, curses.COLOR_GREEN, bg)
        curses.init_pair(_COLOR_NEST, curses.COLOR_MAGENTA, bg)
        return True

    def render(self, simulation: Simulation) -> None:
        """Draw one frame."""
        lines = self._string_renderer.frame_lines(simulation)
        # erase() marks the window as needing to be redrawn
        # but doesn't flash like clear() does.
        self._window.erase()

        max_y, max_x = self._window.getmaxyx()
        for y, line in enumerate(lines):
            if y >= max_y:
                break  # Window too short for the whole frame — clip
            is_status = y == len(lines) - 1
            self._draw_line(y, line, max_x, is_status=is_status)

        self._window.refresh()

    def _draw_line(self, y: int, line: str, max_x: int, is_status: bool) -> None:
        """Draw a single line at row ``y``, truncated to ``max_x``."""
        # Terminals get upset if you write to the very last cell (the
        # cursor may wrap and trigger a scroll). Clip one short of max_x
        # to stay safe.
        safe_line = line[: max_x - 1]

        if is_status:
            self._safe_addstr(y, 0, safe_line, self._attr(_COLOR_STATUS))
            return

        # for grid rows, paint each char with its own color attribute
        for x, ch in enumerate(safe_line):
            attr = self._attr_for_glyph(ch)
            self._safe_addch(y, x, ch, attr)

    def _attr_for_glyph(self, ch: str) -> int:
        if ch == _ANT_GLYPH:
            return self._attr(_COLOR_ANT)
        if ch == _TILE_GLYPHS[TileKind.DIRT]:
            return self._attr(_COLOR_DIRT)
        if ch == _TILE_GLYPHS[TileKind.TUNNEL]:
            return self._attr(_COLOR_TUNNEL)
        if ch == _TILE_GLYPHS[TileKind.ROCK]:
            return self._attr(_COLOR_ROCK)
        if ch == _TILE_GLYPHS[TileKind.FOOD]:
            return self._attr(_COLOR_FOOD)
        if ch == _TILE_GLYPHS[TileKind.NEST]:
            return self._attr(_COLOR_NEST)
        return 0

    def _attr(self, pair_id: int) -> int:
        """Return the curses attribute for a color pair, or 0 if color
        isn't available"""
        return curses.color_pair(pair_id) if self._color_enabled else 0

    def _safe_addstr(self, y: int, x: int, text: str, attr: int) -> None:
        """Write a string, swallowing edge-of-window errors
        Curses raises when you write to the very last cell of the
        window. At the edges this is unavoidable, and the character
        still appears.
        """
        with suppress(curses.error):
            self._window.addstr(y, x, text, attr)

    def _safe_addch(self, y: int, x: int, ch: str, attr: int) -> None:
        with suppress(curses.error):
            self._window.addch(y, x, ch, attr)
