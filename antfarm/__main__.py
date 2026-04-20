"""Entry point for `python -m antfarm` and the `antfarm` console script."""

import sys
import time

from antfarm import __version__, config
from antfarm.renderer import TerminalRenderer
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

    print(f"Ants in the Shell v{__version__}  (Ctrl-C to quit)")
    time.sleep(0.5)

    simulation = Simulation(
        width=config.WORLD_WIDTH,
        height=config.WORLD_HEIGHT,
        starting_ants=config.STARTING_ANTS,
        seed=config.DEFAULT_SEED,
    )
    renderer = TerminalRenderer()

    try:
        while True:
            simulation.tick()
            renderer.render(simulation)
            time.sleep(config.TICK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nGoodbye.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
