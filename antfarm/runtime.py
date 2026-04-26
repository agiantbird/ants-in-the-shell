"""The runtime loop."""

import time
from collections.abc import Callable
from typing import Protocol

from antfarm.commands import Command, NoOp, Quit, SlowDown, SpeedUp, TogglePause
from antfarm.input import InputHandler
from antfarm.simulation import Simulation

# How long a tick should take at speed 1.0.
# Speed 2.0 halves this, speed 0.5 doubles it.
BASE_TICK_SECONDS: float = 0.15


class Renderer(Protocol):
    """Structural interface any renderer must satisfy."""

    def render(self, simulation: Simulation) -> None: ...


class InputSource(Protocol):
    """Anything that can be asked 'What key was just pressed?'

    Returns -1 if no key is pending.
    """
    def __call__(self) -> int: ...


def run(
        simulation: Simulation,
        renderer: Renderer,
        input_source: InputSource,
        input_handler: InputHandler | None = None,
        sleep: Callable[[float], None] | None = None,
        max_ticks: int | None = None,
) -> None:
    """Run the simulation loop until user quits.

    Args:
        simulation: The simulation to advance
        renderer: Called once per loop iteration with the current sim.
        input_source: Called once per loop iteration to get the next
            keypress. Returns -1 if no key is pending.
        sleep: Sleep function. Defaults to ``time.sleep``. Tests pass a
            no-op to skip waiting.
        max_ticks: If set, the loop exits after this many iterations
        regardless of quit commands.
    """
    if input_handler is None:
        input_handler = InputHandler()
    if sleep is None:
        sleep = time.sleep

    iterations = 0
    while True:
        key = input_source()
        command = input_handler.key_to_command(key)

        if _handle_command(command, simulation):
            return  # Command asked us to quit.

        simulation.tick()
        renderer.render(simulation)

        # Sleep duration is inversely proportional to speed.
        sleep(BASE_TICK_SECONDS / simulation.speed)

        iterations += 1
        if max_ticks is not None and iterations >= max_ticks:
            return


def _handle_command(command: Command, simulation: Simulation) -> bool:
    """Apply a command to the simulation.

    Returns:
        True if the command asked to quit, False otherwise
    """
    match command:
        case NoOp():
            return False
        case Quit():
            return True
        case TogglePause():
            simulation.toggle_pause()
            return False
        case SpeedUp():
            simulation.speed_up()
            return False
        case SlowDown():
            simulation.slow_down()
            return False
        case _:
            # Unknown, return NoOp
            return False
