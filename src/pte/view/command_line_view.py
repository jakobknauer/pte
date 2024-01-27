import curses


class CommandLineView:
    def __init__(self, window: curses.window):
        self._window = window
        self.active = False
        self.command = ""

    def draw(self) -> None:
        if not self.active:
            return

        self._window.erase()
        self._window.addstr(0, 0, f":{self.command}")
        self._window.noutrefresh()

    def clear(self) -> None:
        self.command = ""
        self._window.erase()
        self._window.noutrefresh()

    def move(self, y: int, x: int) -> None:
        self._window.mvwin(y, x)
