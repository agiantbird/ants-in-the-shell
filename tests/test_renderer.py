"""Tests for the StringRenderer.

We test ``frame_lines`` directly — it's pure and easy to assert on.
``CursesRenderer`` is not tested here; it talks to a real terminal,
and faking curses well enough to test meaningfully would be more work
than the test is worth.
"""

from antfarm.renderer import StringRenderer
from antfarm.simulation import Simulation


def test_frame_has_one_line_per_row_plus_status():
    sim = Simulation(width=10, height=5, starting_ants=1, seed=0)
    renderer = StringRenderer()

    lines = renderer.frame_lines(sim)

    # One line per world row, plus one status line.
    assert len(lines) == sim.world.height + 1
    # Each grid line is exactly ``width`` characters wide.
    for line in lines[: sim.world.height]:
        assert len(line) == sim.world.width


def test_frame_shows_ant_at_center_on_first_render():
    sim = Simulation(width=11, height=7, starting_ants=1, seed=0)
    renderer = StringRenderer()

    lines = renderer.frame_lines(sim)

    center_x, center_y = 5, 3
    assert lines[center_y][center_x] == "A"


def test_frame_status_line_shows_tick_and_ant_count():
    sim = Simulation(width=5, height=5, starting_ants=2, seed=0)
    sim.tick()
    sim.tick()
    sim.tick()
    renderer = StringRenderer()

    lines = renderer.frame_lines(sim)
    status = lines[-1]

    assert "tick 3" in status
    assert "ants 2" in status


def test_status_line_shows_speed():
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    sim.speed_up()  # 1.0 -> 2.0
    renderer = StringRenderer()

    status = renderer.frame_lines(sim)[-1]
    assert "speed 2x" in status


def test_status_line_shows_paused_state():
    sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
    renderer = StringRenderer()

    running_status = renderer.frame_lines(sim)[-1]
    assert "running" in running_status
    assert "PAUSED" not in running_status

    sim.pause()
    paused_status = renderer.frame_lines(sim)[-1]
    assert "PAUSED" in paused_status
