"""
Entry point for `python -m antfarm` and the `antfarm` console script.
"""

import sys

from antfarm import __version__


def main(argv: list[str] | None = None) -> int:
    """Run the ant farm.

    Args:
        argv: Command-line arguments, defaulting to ``sys.argv[1:]``.
            Taking this as a parameter (rather than reading ``sys.argv`` directly
            makes the function trivial to test.


    Returns:
        process exit code. 0 on success.
    """
    if argv is None:
        argv = sys.argv[1:]

    print(f"Ants in the Shell v{__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
