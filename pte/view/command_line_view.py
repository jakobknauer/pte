import curses


class CommandLineView:
    def __init__(self, window: curses.window):
        self._window = window
        self.active = False
        self.command = ""

    def draw(self):
        if not self.active:
            return

        self._window.addstr(0, 0, f":{self.command}")
        self._window.noutrefresh()
