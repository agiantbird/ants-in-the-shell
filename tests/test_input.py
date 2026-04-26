"""Tests for the input handler."""

import pytest

from antfarm.commands import NoOp, Quit, SlowDown, SpeedUp, TogglePause
from antfarm.input import NO_KEY, InputHandler


@pytest.fixture
def handler():
    """Fresh handler for each test."""
    return InputHandler()


class TestRecognizedKeys:
    def test_q_quits(self, handler):
        assert handler.key_to_command(ord("q")) == Quit()

    def test_capital_q_quits(self, handler):
        assert handler.key_to_command(ord("Q")) == Quit()

    def test_p_toggles_pause(self, handler):
        assert handler.key_to_command(ord("p")) == TogglePause()

    def test_space_toggles_pause(self, handler):
        assert handler.key_to_command(ord(" ")) == TogglePause()

    def test_plus_speeds_up(self, handler):
        assert handler.key_to_command(ord("+")) == SpeedUp()

    def test_equals_also_speeds_up(self, handler):
        """'=' is '+' without shift. Accept both."""
        assert handler.key_to_command(ord("=")) == SpeedUp()

    def test_minus_slows_down(self, handler):
        assert handler.key_to_command(ord("-")) == SlowDown()

    def test_underscore_also_slows_down(self, handler):
        """'_' is '-' without shift. Accept both."""
        assert handler.key_to_command(ord("_")) == SlowDown()


class TestUnrecognized:
    def test_no_key_returns_noop(self, handler):
        assert handler.key_to_command(NO_KEY) == NoOp()

    def test_unrelated_key_returns_noop(self, handler):
        assert handler.key_to_command(ord("x")) == NoOp()

    def test_nonprintable_key_returns_noop(self, handler):
        # Curses sometimes gives back large ints for special keys (arrow
        # keys, for example)
        assert handler.key_to_command(1000) == NoOp()

    def test_negative_other_than_no_key_returns_noop(self, handler):
        assert handler.key_to_command(-999) == NoOp()
