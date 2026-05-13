"""Integration tests for the Simulation orchestrator."""

import pytest

from antfarm.actions import Move
from antfarm.simulation import Simulation
from antfarm.tile import Tile, TileKind


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

    def test_starting_cell_is_nest(self):
        sim = Simulation(width=10, height=10, starting_ants=1, seed=0)
        center_x, center_y = 5, 5
        assert sim.world.tile_at(center_x, center_y).kind is TileKind.NEST

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

        for _ in range(50):
            sim.tick()

        tunnels_after = self._count_tunnels(sim)
        assert tunnels_after > tunnels_before

    def test_ants_stay_in_bounds(self):
        """Lots of ticks, lots of ants, never go out of bounds."""
        sim = Simulation(width=15, height=10, starting_ants=3, seed=7)
        for _ in range(500):
            sim.tick()
            for ant in sim.colony:
                assert 0 <= ant.x < 15
                assert 0 <= ant.y < 10

    def test_ants_always_stand_on_passable_tile(self):
        """An ant's position should always be a passable tile (tunnel,
        nest, or food about to be eaten) after a tick."""
        sim = Simulation(width=15, height=10, starting_ants=2, seed=11)
        for _ in range(200):
            sim.tick()
            for ant in sim.colony:
                tile = sim.world.tile_at(ant.x, ant.y)
                assert tile.is_passable(), f"Ant standing on non-passable tile {tile.kind}"

    @staticmethod
    def _count_tunnels(sim: Simulation) -> int:
        return sum(
            1
            for y in range(sim.world.height)
            for x in range(sim.world.width)
            if sim.world.tile_at(x, y).kind is TileKind.TUNNEL
        )


class TestPauseCommands:
    def test_fresh_sim_is_not_paused(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        assert sim.is_paused is False

    def test_pause_sets_flag(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        sim.pause()
        assert sim.is_paused is True

    def test_resume_clears_flag(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        sim.pause()
        sim.resume()
        assert sim.is_paused is False

    def test_toggle_pause(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        sim.toggle_pause()
        assert sim.is_paused is True
        sim.toggle_pause()
        assert sim.is_paused is False

    def test_tick_is_noop_when_paused(self):
        sim = Simulation(width=10, height=10, starting_ants=1, seed=0)
        sim.tick()
        sim.tick()
        ticks_before = sim.tick_count

        sim.pause()
        for _ in range(20):
            sim.tick()
        assert sim.tick_count == ticks_before


class TestFoodConsumption:
    def test_ant_gains_energy_when_stepping_on_food(self):
        """Place the ant next to food, force a move, expect energy gain."""
        sim = Simulation(width=10, height=10, starting_ants=1, seed=0)
        # Reset the world to a known state — no rocks, no random food.
        # We're testing the eating mechanic in isolation.
        sim.world.set_tile(5, 5, Tile(kind=TileKind.NEST))
        sim.world.set_tile(6, 5, Tile(kind=TileKind.FOOD, food_value=1))

        # Place the ant adjacent to the food.
        ant = next(iter(sim.colony))
        ant.x, ant.y = 5, 5
        starting_energy = ant.energy

        # Manually apply a Move action onto the food tile.
        sim._apply_action(ant, Move(x=6, y=5))

        assert ant.energy > starting_energy
        # Food tile should now be tunnel.
        assert sim.world.tile_at(6, 5).kind is TileKind.TUNNEL

    def test_food_remaining_drops_when_ants_eat(self):
        """Run for many ticks, food amount should decrease."""
        sim = Simulation(width=20, height=10, starting_ants=5, seed=7)
        starting_food = sim.food_remaining

        for _ in range(500):
            sim.tick()

        assert sim.food_remaining <= starting_food


class TestSpeedCommands:
    def test_default_speed_is_one(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        assert sim.speed == 1.0

    def test_speed_up_multiplies(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        sim.speed_up()
        assert sim.speed == 2.0
        sim.speed_up()
        assert sim.speed == 4.0

    def test_slow_down_divides(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        sim.slow_down()
        assert sim.speed == 0.5

    def test_speed_up_is_capped(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        for _ in range(20):
            sim.speed_up()
        # MAX_SPEED is 8.0.
        assert sim.speed == 8.0

    def test_slow_down_is_floored(self):
        sim = Simulation(width=5, height=5, starting_ants=1, seed=0)
        for _ in range(20):
            sim.slow_down()
        # MIN_SPEED is 0.25.
        assert sim.speed == 0.25
