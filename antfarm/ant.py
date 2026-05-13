"""The ``Ant`` – an individual ant in the colony.

An ant has a position and a random number generator.
Each tick, it perceives the world locally (its four neighbors) and
decides on an ``Action``. The ant itself never mutates the world – it
only describes what it wants to do.
"""

import random
from dataclasses import dataclass, field

from antfarm.actions import Action, Dig, Idle, Move
from antfarm.world import World

# The four cardinal direction offsets. Kept as a module-level constant
# so that it's shared and not rebuilt every tick
_NEIGHBOR_OFFSETS: tuple[tuple[int, int], ...] = (
    (0, -1),  # up
    (0, 1),   # down
    (-1, 0),  # left
    (1, 0),   # right
)

@dataclass
class Ant:
    """A single ant.

    Attributes:
        x, y: Current position.
        rng: Random number generator uses for decision-making. Each ant
            gets its own RNG so that adding or removing ants doesn't peturb
            the sequence another ant would have seen.
        age: ticks this ant has been alive
        energy: How much fuel the ant has. Eating food directly raises energy.
        carrying_food: True when the ant has picked up food but not yet deposited it at the nest.
    """

    x: int
    y: int
    rng: random.Random = field(repr=False)
    age: int = 0
    energy: int = 0
    carrying_food: bool = False

    def step(self, world: World) -> Action:
        """Decide what this ant does this tick."""
        # Shuffle the four offsets and try them in order. Using
        # ``self.rng.sample`` rather than ``random.sample`` keeps the
        # behavior deterministic given the seed.
        ordered = self.rng.sample(_NEIGHBOR_OFFSETS, k=len(_NEIGHBOR_OFFSETS))
        # dx, dy (delta x, delta y)
        # nx, ny (new X, new y)
        # If ant is at (5, 5) and tries (dx, dy) = (1, 0):
        # nx = 5 + 1 = 6
        # ny = 5 + 0 = 5
        # ant moves one square to the right
        for dx, dy in ordered:
            nx, ny = self.x + dx, self.y + dy
            if not world.in_bounds(nx, ny):
                continue
            tile = world.tile_at(nx, ny)
            if tile.is_passable():
                return Move(x=nx, y=ny)
            if tile.is_diggable():
                return Dig(x=nx, y=ny)
        # boxed in on all sides. Do nothing this tick.
        return Idle()
