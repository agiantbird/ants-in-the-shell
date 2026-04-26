"""Entry point for `python -m antfarm` and the `antfarm` console script.

This main file:
1. Parses command line arguments
2. Sets up the curses library safely via ``curses.wrapper``
3. Hands a simulation, renderer, and input source to the runtime loop

The ``curses.wrapper`` function is critical, it:
1. Initializes curses
2. Configures the terminal into the unusual state curses requires
    (raw mode, no echo, cbreak)
3. Restores the terminal on exit, even if the code crashes
"""

import curses
import sys

from antfarm import __version__, config
from antfarm.renderer import CursesRenderer
from antfarm.runtime import run
from antfarm.simulation import Simulation


def main(argv: list[str] | None = None) -> int:
    """Run the ant farm.

    Args:
        argv: Command-line arguments, defaulting to ``sys.argv[1:]``.
            Taking this as a parameter (rather than reading ``sys.argv``
            directly) makes the function trivial to test.

    Returns:
        Process exit code. 0 on success, 130 on Ctrl-C.
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        curses.wrapper(_curses_main)
    except KeyboardInterrupt:
        return 130

    return 0


def _curses_main(stdscr: "curses.window") -> None:
    """The function curses.wrapper calls with an initialized window

    ``stdscr`` is the top-level curses window covering the terminal.
    Configured for non-blocking input, it builds the simulation and renderer
    then hands control to ``run``
    """
    # nodelay(True) makes window.getch() return immediately, this
    # keeps the sim running while listening for input
    stdscr.nodelay(True)

    # keypad(True) translates multi-byte escape sequences (arrow keys,
    # function keys, etc.) into single curses constants.
    stdscr.keypad(True)

    # Show a brief startup message before the sim takes over the screen
    stdscr.addstr(0, 0, f"Ants in the Shell v{__version__}")
    stdscr.addstr(1, 0, "Starting...")
    stdscr.refresh()

    simulation = Simulation(
        width=config.WORLD_WIDTH,
        height=config.WORLD_HEIGHT,
        starting_ants=config.STARTING_ANTS,
        seed=config.DEFAULT_SEED,
    )
    renderer = CursesRenderer(stdscr)

    # The input source is just "ask the window what key was pressed"
    # the runtime loop only cares that it gets an int back
    def input_source() -> int:
        return stdscr.getch()

    run(simulation, renderer, input_source)


if __name__ == "__main__":
    raise SystemExit(main())
