"""
Tunable constants for the simulation.
"""

from typing import Final

# Grid dimensions (columns, rows)
WORLD_WIDTH: Final[int] = 60
WORLD_HEIGHT: Final[int] = 20

# How many ants the colony starts with
STARTING_ANTS: Final[int] = 1

# Seconds between simulation ticks when running interactively
# Note: tests don't use this but instead call step() directly
TICK_INTERVAL_SECONDS: Final[float] = 0.1

# Default Random Number Generator (RNG) seed
# ``None`` means "use system entropy"
# pass an int for reproducible runs, such as during debugging.
DEFAULT_SEED: int | None = None
