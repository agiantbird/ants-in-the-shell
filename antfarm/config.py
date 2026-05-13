"""
Tunable constants for the simulation.
"""

from typing import Final

# -- World Dimensions ----------------------------------------------
# Grid dimensions (columns, rows)
WORLD_WIDTH: Final[int] = 60
WORLD_HEIGHT: Final[int] = 20

# -- Colony ----------------------------------------------

# How many ants the colony starts with
STARTING_ANTS: Final[int] = 3

# Energy a new ant has
STARTING_ENERGY: Final[int] = 100

# Energy gained from eating one unit of food directly
SCOUT_REWARD: Final[int] = 10

# -- World generation ----------------------------------------------

# Each rock starts at a random tile and 'walks' for this many steps, making
# an organic-looking formation
ROCK_BLOB_COUNT: Final[int] = 8
ROCK_BLOB_LENGTH: Final[int] = 12

# Food spawns in clusters, a center tile and a few neighbors.
# Food clusters are scattered throughout the world
FOOD_CLUSTER_COUNT: Final[int] = 6
FOOD_CLUSTER_SIZE: Final[int] = 3  # Tiles per cluster
FOOD_VALUE_PER_TILE: Final[int] = 1

# How big a clear ring around the nest the world generator should
# preserve. Without this, ants might spawn surrounded by rocks.
NEST_CLEAR_RADIUS: Final[int] = 2

# -- Runtime ----------------------------------------------

# Default Random Number Generator (RNG) seed
# ``None`` means "use system entropy"
# pass an int for reproducible runs, such as during debugging.
DEFAULT_SEED: int | None = None

# still need?

# Seconds between simulation ticks when running interactively
# Note: tests don't use this but instead call step() directly
# TICK_INTERVAL_SECONDS: Final[float] = 0.1
