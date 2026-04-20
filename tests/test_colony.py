"""Tests for the Colony class."""

import random

from antfarm.ant import Ant
from antfarm.colony import Colony


def _ant(x: int = 0, y: int = 0) -> Ant:
    return Ant(x=x, y=y, rng=random.Random(0))


def test_empty_colony():
    colony = Colony()
    assert len(colony) == 0
    assert list(colony) == []


def test_add_increases_length():
    colony = Colony()
    colony.add(_ant())
    colony.add(_ant())
    assert len(colony) == 2


def test_iteration_is_snapshot():
    """Iterating should be safe even if the caller mutates the colony."""
    colony = Colony([_ant(), _ant(), _ant()])

    seen = 0
    for _ant_in_loop in colony:
        colony.add(_ant())  # would break if iteration wasn't snapshotted
        seen += 1

    assert seen == 3  # We saw the original three, not the new additions.
    assert len(colony) == 6
