"""The ``Simulation``, acts as the orchestrator

Owns a ``World`` and a ``Colony``. On each tick, asks every ant for an
``Action``, then applies those actions to the world. The simulation
mutates the world based on ant decisions.

Deterministic based on a given seed: same seed + same initial conditions
+ same number of ticks = same resulting state.
"""

import random

from antfarm.actions import Dig, Idle, Move
from antfarm.ant import Ant
from antfarm.colony import Colony
from antfarm.exceptions import TileNotDiggableError
from antfarm.tile import Tile, TileKind
from antfarm.world import World


class Simulation:
    """The top-level simulation object."""

    def __init__(
            self,
            width: int,
            height: int,
            starting_ants: int = 1,
            seed: int | None = None,
    ) -> None:
        if starting_ants < 1:
            raise ValueError(f"starting_ants must be at least 1, got {starting_ants}")

        self.tick_count: int = 0
        self._rng = random.Random(seed)
        self.world = World(width=width, height=height)
        self.colony = Colony()

        self._seed_colony(starting_ants)

    def _seed_colony(self, count: int) -> None:
        """Place the initial ants in the center of the world.

        Converts the center tile to tunnel so ants have somewhere to stand.
        """
        center_x = self.world.width // 2
        center_y = self.world.height // 2

        self.world.set_tile(center_x, center_y, Tile(kind=TileKind.TUNNEL))

        for _ in range(count):
            # Each ant gets its own random number generator, derived from the root RNG
            ant_rng = random.Random(self._rng.random())
            self.colony.add(Ant(x=center_x, y=center_y, rng=ant_rng))

    def tick(self) -> None:
        """Advance the simulation by one step."""
        for ant in self.colony:
            action = ant.step(self.world)
            self._apply_action(ant, action)

        self.tick_count += 1

    def _apply_action(self, ant: Ant, action: object) -> None:
        """Apply a single ant's action to the world."""
        match action:
            case Idle():
                pass

            case Move(x=x, y=y):
                if not self.world.in_bounds(x, y):
                    raise ValueError(f"Ant tried to move out of bounds to ({x}, {y})")
                if not self.world.tile_at(x, y).is_passable():
                    raise ValueError(f"Ant tried to move into non-passable tile at ({x}, {y})")
                ant.x, ant.y = x, y

            case Dig(x=x, y=y):
                try:
                    self.world.dig(x, y)
                except TileNotDiggableError:
                    raise

            case _:
                raise TypeError(f"Unknown action type: {type(action).__name__}")
