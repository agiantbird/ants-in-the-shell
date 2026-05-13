"""The ``Simulation``, acts as the orchestrator

Owns a ``World`` and a ``Colony``. On each tick, asks every ant for an
``Action``, then applies those actions to the world. The simulation
mutates the world based on ant decisions.

Deterministic based on a given seed: same seed + same initial conditions
+ same number of ticks = same resulting state.
"""

import random

from antfarm import config, worldgen
from antfarm.actions import Dig, Idle, Move
from antfarm.ant import Ant
from antfarm.colony import Colony
from antfarm.exceptions import TileNotDiggableError
from antfarm.tile import TileKind
from antfarm.world import World

# Speed expressed as a multiplier with 1.0 as the default rate.
# Doubling the speed halves the time between ticks.
MIN_SPEED: float = 0.25
MAX_SPEED: float = 8.0
SPEED_STEP: float = 2.0


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

        # Runtime state controllable via the command API
        self._paused: bool = False
        self._speed: float = 1.0

        self._seed_colony(starting_ants)

    def _seed_colony(self, count: int) -> None:
        """Place the initial ants in the center of the world.

        Converts the center tile to tunnel so ants have somewhere to stand.
        """
        center_x = self.world.width // 2
        center_y = self.world.height // 2

        # Generate world before placing ants
        worldgen.generate(self.world, self._rng, center_x, center_y)

        # Place ants
        for _ in range(count):
            ant_rng = random.Random(self._rng.random())
            self.colony.add(
                Ant(
                    x=center_x,
                    y=center_y,
                    rng=ant_rng,
                    energy=config.STARTING_ENERGY,
                )
            )


    # -- command API ---------------------------------------------------

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def speed(self) -> float:
        return self._speed

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def toggle_pause(self) -> None:
        self._paused = not self._paused

    def speed_up(self) -> None:
        """Multiply speed by ``SPEED_STEP``, capped at ``MAX_SPEED``."""
        self._speed = min(self._speed * SPEED_STEP, MAX_SPEED)

    def slow_down(self) -> None:
        """Divide speed by ``SPEED_STEP``, capped at ``MIN_SPEED``."""
        self._speed = max(self._speed / SPEED_STEP, MIN_SPEED)

    # ------------------------------------------------------------------

    def tick(self) -> None:
        """Advance the simulation by one step.
        If the simulaton is paused, this is a no-op. Pause handling lives here.
        """
        if self._paused:
            return

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
                self._maybe_eat(ant)

            case Dig(x=x, y=y):
                try:
                    self.world.dig(x, y)
                except TileNotDiggableError:
                    raise

            case _:
                raise TypeError(f"Unknown action type: {type(action).__name__}")

    def _maybe_eat(self, ant: Ant) -> None:
        """If the ant just stepped onto a food tile, eat the food."""
        tile = self.world.tile_at(ant.x, ant.y)
        if not tile.is_food():
            return

        # eat food
        ant.energy += config.SCOUT_REWARD
        # convert food tile to tunnel
        tile.food_value = 0
        tile.kind = TileKind.TUNNEL

    @property
    def food_remaining(self) -> int:
        """Total food left in the world."""
        return sum(
            self.world.tile_at(x, y).food_value
            for y in range(self.world.height)
            for x in range(self.world.width)
        )
