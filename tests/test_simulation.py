"""Integration tests for the Simulation orchestrator."""

import pytest

from antfarm.simulation import Simulation
from antfarm.tile import TileKind


class TestConstruction:
    def test_seed_is_deterministic(self):
        """Same seed produces identical simulation state after N ticks."""
        a = Simulation(width=10, height=10, starting_ants=1, seed=42)
        b = Simulation(width=10, height=10, starting_ants=1, seed=42)

        for _ in range(100):
            a.tick()
            b.tick()

        # All tiles match.
        for y in range(10):
            for x in range(10):
                assert a.world.tile_at(x, y).kind is b.world.tile_at(x, y).kind
        # All ants are at matching positions.
        a_ants = sorted((ant.x, ant.y) for ant in a.colony)
        b_ants = sorted((ant.x, ant.y) for ant in b.colony)
        assert a_ants == b_ants

    def test_different_seeds_diverge(self):
        """Different seeds should produce different outcomes within a few ticks."""
        a = Simulation(width=10, height=10, starting_ants=1, seed=1)
        b = Simulation(width=10, height=10, starting_ants=1, seed=2)

        for _ in range(20):
            a.tick()
            b.tick()

        a_ant = next(iter(a.colony))
        b_ant = next(iter(b.colony))
        assert (a_ant.x, a_ant.y) != (b_ant.x, b_ant.y)

    def test_starting_cell_is_tunnel(self):
        sim = Simulation(width=10, height=10, starting_ants=1, seed=0)
        center_x, center_y = 5, 5
        assert sim.world.tile_at(center_x, center_y).kind is TileKind.TUNNEL

    def test_rejects_zero_starting_ants(self):
        with pytest.raises(ValueError, match="starting_ants"):
            Simulation(width=10, height=10, starting_ants=0)


class TestTick:
    def test_tick_advances_counter(self):
        sim = Simulation(width=10, height=10, starting_ants=1, seed=0)
        assert sim.tick_count == 0
        sim.tick()
        assert sim.tick_count == 1
        sim.tick()
        assert sim.tick_count == 2

    def test_ant_digs_tunnels_over_time(self):
        """After many ticks the ant should have dug more than just the start tile."""
        sim = Simulation(width=10, height=10, starting_ants=1, seed=0)

        # count tunnels before (just the starting cell)
        tunnels_before = self._count_tunnels(sim)
        assert tunnels_before == 1

        for _ in range(50):
            sim.tick()

        tunnels_after = self._count_tunnels(sim)
        assert tunnels_after > tunnels_before

    def test_ants_always_stand_on_tunnel(self):
        """An ant's position should always be a tunnel tile after a tick."""
        sim = Simulation(width=15, height=10, starting_ants=2, seed=11)
        for _ in range(200):
            sim.tick()
            for ant in sim.colony:
                assert sim.world.tile_at(ant.x, ant.y).kind is TileKind.TUNNEL

    @staticmethod
    def _count_tunnels(sim: Simulation) -> int:
        return sum(
            1
            for y in range(sim.world.height)
            for x in range(sim.world.width)
            if sim.world.tile_at(x, y).kind is TileKind.TUNNEL
        )
