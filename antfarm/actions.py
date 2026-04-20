"""Actions – What an ant can decide to do on a given tick.

Each ``Ant.step()`` returns an ``Action`` describing its intent.
The ``Simulation`` is responsible for applying actions to the world.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """Marker base class. Never instantiated directly."""


@dataclass(frozen=True)
class Idle(Action):
    """The ant does nothing this tick."""


@dataclass(frozen=True)
class Move(Action):
    """The ant moves into an adjacent tunnel tile at ``(x, y)``.

    The ant's current position is not part of the action — the simulation
    knows which ant produced the action and can look it up.
    """
    x: int
    y: int


@dataclass(frozen=True)
class Dig(Action):
    """The ant digs the tile at ``(x, y)``, turning it into a tunnel.

    Unlike ``Move``, this doesn't change the ant's position, an ant digs, then moves.
    """

    x: int
    y: int
