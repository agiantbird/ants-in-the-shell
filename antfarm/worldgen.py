"""World generation"""

import random

from antfarm import config
from antfarm.tile import Tile, TileKind
from antfarm.world import World

# Cardinal-direction offsets for random walks
_NEIGHBOR_OFFSETS: tuple[tuple[int, int], ...] = (
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0)
)


def generate(world: World, rng: random.Random, nest_x: int, nest_y: int) -> None:
    """Populate ``world`` withrocks, food and nest tile(s)"""
    _place_nest(world, nest_x, nest_y)
    _place_rocks(world, rng, nest_x, nest_y)
    _place_food(world, rng, nest_x, nest_y)


def _place_nest(world: World, nest_x: int, nest_y: int) -> None:
    """Set the central tile to be the nest with a buffer of tunnel tiles around it."""
    world.set_tile(nest_x, nest_y, Tile(kind=TileKind.NEST))
    # Clear area around nest so ants have somewhere to step on first clock tick
    for dx, dy in _NEIGHBOR_OFFSETS:
        nx, ny = nest_x + dx, nest_y + dy
        if world.in_bounds(nx, ny):
            world.set_tile(nx, ny, Tile(kind=TileKind.TUNNEL))


def _place_rocks(
        world: World,
        rng: random.Random,
        nest_x: int,
        nest_y: int
) -> None:
    """Scatter rocks around the world."""
    for _ in range(config.ROCK_BLOB_COUNT):
        start = _random_dirt_tile_far_from_nest(world, rng, nest_x, nest_y)
        if start is None:
            # World is too full to find a placement for rocks, give up gracefully
            continue

        x, y = start
        for _ in range(config.ROCK_BLOB_LENGTH):
            if not _is_safe_for_obstacle(world, x, y, nest_x, nest_y):
                break
            world.set_tile(x, y, Tile(kind=TileKind.ROCK))

            # Move one tile in a random direction to cluster rock tiles into randomish groups
            x, y = _random_step(x, y, rng, world)


def _place_food(
        world: World,
        rng: random.Random,
        nest_x: int,
        nest_y: int
) -> None:
    """Place clusters of food around the world."""
    for _ in range(config.FOOD_CLUSTER_COUNT):
        start = _random_dirt_tile_far_from_nest(world, rng, nest_x, nest_y)
        if start is None:
            continue

        x, y = start
        placed = 0

        while placed < config.FOOD_CLUSTER_SIZE:
            if not _is_safe_for_food(world, x, y, nest_x, nest_y):
                break
            world.set_tile(
                x,
                y,
                Tile(kind=TileKind.FOOD, food_value=config.FOOD_VALUE_PER_TILE),
            )
            placed += 1
            x, y = _random_step(x, y, rng, world)


# helper functions


def _random_dirt_tile_far_from_nest(
        world: World,
        rng: random.Random,
        nest_x: int,
        nest_y: int,
        max_attempts: int = 100,
) -> tuple[int, int] | None:
    """Pick a random dirt tile outside of the nest's buffer perimeter."""
    for _ in range(max_attempts):
        x = rng.randrange(world.width)
        y = rng.randrange(world.height)
        if not _is_safe_for_obstacle(world, x, y, nest_x, nest_y):
            continue
        return (x, y)
    return None


def _is_safe_for_obstacle(
        world: World,
        x: int,
        y: int,
        nest_x: int,
        nest_y: int,
) -> bool:
    """True if a rock can be placed in this location."""
    if not world.in_bounds(x, y):
        return False
    if _within_nest_radius(x, y, nest_x, nest_y):
        return False
    return world.tile_at(x, y).kind is TileKind.DIRT


def _is_safe_for_food(
        world: World,
        x: int,
        y: int,
        nest_x: int,
        nest_y: int,
) -> bool:
    """True if a food tile can go here.

    Same constraints as rocks: must be dirt, must not be in the nest
    clearing.
    """
    return _is_safe_for_obstacle(world, x, y, nest_x, nest_y)


def _within_nest_radius(x: int, y: int, nest_x: int, nest_y: int) -> bool:
    """True if (x, y) is within the protected radius of the nest.

    Uses Chebyshev distance."""
    return (
        abs(x - nest_x) <= config.NEST_CLEAR_RADIUS and abs(y - nest_y) <= config.NEST_CLEAR_RADIUS
    )


def _random_step(
        x: int,
        y: int,
        rng: random.Random,
        world: World,
) -> tuple[int, int]:
    """Take a random (in-bounds) step from (x, y).

    Return current position if the chosen direction would lead to a step that would leave map."""
    dx, dy = rng.choice(_NEIGHBOR_OFFSETS)
    nx, ny = x + dx, y + dy
    if not world.in_bounds(nx, ny):
        return (x, y)
    return (nx, ny)
