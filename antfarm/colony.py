"""The ``Colony`` – the population of ants."""

from collections.abc import Iterator

from antfarm.ant import Ant


class Colony:
    """A collection of ants."""

    def __init__(self, ants: list[Ant] | None = None) -> None:
        self._ants: list[Ant] = list(ants) if ants else []

    def __len__(self) -> int:
        return len(self._ants)

    def __iter__(self) -> Iterator[Ant]:
        # Iterating over a snapshot (``list(self._ants)``) lets callers
        # mutate the colony during iteration without breaking things
        return iter(list(self._ants))

    def add(self, ant: Ant) -> None:
        self._ants.append(ant)
