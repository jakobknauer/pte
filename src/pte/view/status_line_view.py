import curses

from pte import colors


class StatusLineView:
    def __init__(self, window: curses.window):
        self._window = window
        self.status = ""
        self.status_color: colors.Color = colors.DEFAULT

    def draw(self, *, bottom_line_right: str = "") -> None:
        self._window.erase()
        self._window.addstr(
            0,
            0,
            f" {self.status} ",
            curses.color_pair(self.status_color) ^ curses.A_REVERSE ^ curses.A_BOLD,
        )
        self._window.addstr(
            0,
            self.window_width - 1 - len(bottom_line_right),
            bottom_line_right,
        )
        self._window.noutrefresh()

    @property
    def window_height(self) -> int:
        return self._window.getmaxyx()[0]

    @property
    def window_width(self) -> int:
        return self._window.getmaxyx()[1]

    def move(self, y: int, x: int) -> None:
        self._window.mvwin(y, x)
