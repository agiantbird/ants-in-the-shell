"""Smoke tests for the package itself — proves the test harness works
and the entry point is reachable."""

import antfarm
from antfarm.__main__ import main


def test_package_has_version():
    """The package exposes a version string."""
    assert isinstance(antfarm.__version__, str)
    assert antfarm.__version__  # non-empty


def test_main_returns_zero_on_no_args(capsys):
    """Invoking main() with no args should succeed and print something.

    ``capsys`` is a pytest fixture that captures stdout/stderr. Pytest
    injects it based on the parameter name — that's why we don't import it.
    """
    exit_code = main(argv=[])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Ants in the Shell" in captured.out
