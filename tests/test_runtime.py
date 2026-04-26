"""Tests for the runtime loop."""

from antfarm.input import NO_KEY
from antfarm.runtime import run
from antfarm.simulation import Simulation


class FakeRenderer:
    """A renderer that records the ticks it was called with."""

    def __init__(self):
        self.tick_counts: list[int] = []

    def render(self, simulation):
        self.tick_counts.append(simulation.tick_count)


class KeyQueue:
    """An input source that yields keys from a predetermined queue."""

    def __init__(self, keys: list[int]):
        self._keys = list(keys)

    def __call__(self) -> int:
        if not self._keys:
            return NO_KEY
        return self._keys.pop(0)


def _no_sleep(_seconds: float) -> None:
    pass


def test_run_quits_on_q():
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    renderer = FakeRenderer()
    keys = KeyQueue([ord("q")])

    run(sim, renderer, keys, sleep=_no_sleep)

    # The loop should have exited before render, quit is checked
    # before tick/render
    assert renderer.tick_counts == []


def test_run_respects_max_ticks():
    """With no quit command, max_tickets should bound the loop."""
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    renderer = FakeRenderer()
    keys = KeyQueue([]) # no keys pressed

    run(sim, renderer, keys, sleep=_no_sleep, max_ticks=5)

    assert len(renderer.tick_counts) == 5
    assert sim.tick_count == 5


def test_run_pauses_and_resumes():
    """Pressing 'p' pauses; while paused, ticks don't advance"""
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    renderer = FakeRenderer()
    # press 'p' at interation 0 (pauses), then no keys for the rest
    keys = KeyQueue([ord("p")])

    run(sim, renderer, keys, sleep=_no_sleep, max_ticks=5)

    # Renderer was called 5 times but the sim was paused for all of them: tick count
    # should remain at 0
    assert len(renderer.tick_counts) == 5
    assert sim.tick_count == 0
    assert sim.is_paused is True


def test_run_speed_up_changes_sim_speed():
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    renderer = FakeRenderer()
    keys = KeyQueue([ord("+"), ord("=")])

    run(sim, renderer, keys, sleep=_no_sleep, max_ticks=3)
    assert sim.speed == 4.0  # 1.0 (default speed) * 2 * 2


def test_run_slow_down_changes_sim_speed():
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    renderer = FakeRenderer()
    keys = KeyQueue([ord("-")])

    run(sim, renderer, keys, sleep=_no_sleep, max_ticks=2)

    assert sim.speed == 0.5


def test_run_unknown_keys_are_harmless():
    """Typing random keys shouldn't break the loop."""
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    renderer = FakeRenderer()
    keys = KeyQueue([ord("x"), ord("z"), ord("!")])

    run(sim, renderer, keys, sleep=_no_sleep, max_ticks=3)

    assert len(renderer.tick_counts) == 3
    assert sim.tick_count == 3
