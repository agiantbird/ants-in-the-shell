"""Commands - what a user keypress can ask the simulation to do."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    """Marker base class. Never instantiated directly."""


@dataclass(frozen=True)
class NoOp(Command):
    """Nothing to do. Used when a keypress has no mapping, or when
    no key was pressed at all."""


@dataclass(frozen=True)
class Quit(Command):
    """Stop the runtime loop and exit the program."""


@dataclass(frozen=True)
class TogglePause(Command):
    """Flip the simulation's paused state"""


@dataclass(frozen=True)
class SpeedUp(Command):
    """Increase tick rate."""


@dataclass(frozen=True)
class SlowDown(Command):
    """Decreate tick rate."""
