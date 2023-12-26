import curses


class CommandLineView:
    def __init__(self, window: curses.window):
        self._window = window
        self.active = False
        self.command = ""

    def draw(self):
        if not self.active:
            return

        self._window.erase()
        self._window.addstr(0, 0, f":{self.command}")
        self._window.noutrefresh()

    def clear(self):
        self.command = ""
        self._window.erase()
        self._window.noutrefresh()
