"""Input handling - turns keypresses into ``Command` objects."""

from antfarm.commands import Command, NoOp, Quit, SlowDown, SpeedUp, TogglePause

# Curses returns -1 from getch when no key was pressed.
NO_KEY: int = -1


class InputHandler:
    """Maps a raw keycode to a ``Command``."""

    def key_to_command(self, key: int) -> Command:
        """Translate a keypress into a command.
        Args:
            key: The keycode, as returned by ``curses.getch()``. Use
            ``-1`` (``NO_KEY``) to represent "no key pressed."

        Returns:
            The command corresponding to the keypress, or ``NoOp()`` for
            unrecognized or absent keys.
        """
        if key == NO_KEY:
            return NoOp()

        # Convert to a character if it's a printable keycode.
        try:
            ch = chr(key)
        except ValueError:
            return NoOp()

        if ch in ("q", "Q"):
            return Quit()
        if ch in ("p", "P", " "):
            return TogglePause()
        if ch in ("+", "="):
            return SpeedUp()
        if ch in ("_", "-"):
            return SlowDown()

        return NoOp()
