"""Tests for TerminalRenderer."""

from antfarm.renderer import TerminalRenderer
from antfarm.simulation import Simulation


def test_frame_has_one_line_per_row_plus_status():
    sim = Simulation(width=10, height=5, starting_ants=1, seed=0)
    renderer = TerminalRenderer()

    lines = renderer._frame_lines(sim)

    # One line per world row, plus one status line
    assert len(lines) == sim.world.height + 1
    # each grid line is exactly ``width`` characters wide
    for line in lines[: sim.world.height]:
        assert len(line) == sim.world.width


def test_frame_shows_ant_at_center_on_first_render():
    sim = Simulation(width=11, height=7, starting_ants=1, seed=0)
    renderer = TerminalRenderer()

    lines = renderer._frame_lines(sim)

    center_x, center_y = 5, 3
    assert lines[center_y][center_x] == "A"


def test_frame_status_line_shows_tick_and_ant_count():
    sim = Simulation(width=5, height=5, starting_ants=2, seed=0)
    sim.tick()
    sim.tick()
    sim.tick()
    renderer = TerminalRenderer()

    lines = renderer._frame_lines(sim)
    status = lines[-1]

    assert "tick 3" in status
    assert "ants 2" in status
