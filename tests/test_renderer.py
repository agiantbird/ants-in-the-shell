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


def test_status_line_shows_food_remaining():
    sim = Simulation(width=20, height=10, starting_ants=1, seed=0)
    renderer = StringRenderer()

    status = renderer.frame_lines(sim)[-1]
    assert f"food {sim.food_remaining}" in status


def test_status_line_shows_colony_reserves():
    sim = Simulation(width=10, height=10, starting_ants=1, seed=0)
    renderer = StringRenderer()

    status = renderer.frame_lines(sim)[-1]
    assert "reserves 0" in status


def test_frame_renders_nest_glyph():
    """The nest tile should appear in rendered output at the start."""
    sim = Simulation(width=10, height=10, starting_ants=1, seed=0)
    renderer = StringRenderer()

    # The nest tile is at (5, 5), but the ant is also there at tick 0.
    # So, check that the nest is there when the ant has wandered off.
    sim.tick()
    sim.tick()
    sim.tick()
    lines = renderer.frame_lines(sim)
    grid_text = "\n".join(lines[:-1])  # exclude status line

    assert("@" in grid_text)  # '@' is the nest glyph


def test_frame_renders_rock_and_food():
    """Rocks and food should be visible in rendered output."""
    sim = Simulation(width=30, height=15, starting_ants=1, seed=0)
    renderer = StringRenderer()

    lines = renderer.frame_lines(sim)
    grid_text = "\n".join(lines[:-1])

    assert "R" in grid_text
    assert "F" in grid_text
