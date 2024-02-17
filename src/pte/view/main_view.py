import curses

from .command_line_view import CommandLineView
from .document_view import DocumentView
from .status_line_view import StatusLineView


class MainView:
    def __init__(self, window: curses.window):
        self._window = window
        self._window.timeout(25)

        # pylint: disable=no-member
        document_window = window.derwin(curses.LINES - 2, curses.COLS, 0, 0)
        status_line_window = window.derwin(1, curses.COLS, curses.LINES - 2, 0)
        command_line_window = window.derwin(1, curses.COLS, curses.LINES - 1, 0)

        self.document_view = DocumentView(document_window)
        self.status_line_view = StatusLineView(status_line_window)
        self.command_line_view = CommandLineView(command_line_window)

    def draw(self, *, show_cursor: bool = True, bottom_line_right: str = "") -> None:
        self._window.noutrefresh()
        self.status_line_view.draw(bottom_line_right=bottom_line_right)
        self.document_view.draw()
        self.command_line_view.draw()

        curses.curs_set(1 if show_cursor else 0)

        curses.doupdate()

    def read(self) -> str:
        try:
            while (key := self._window.getkey()) == "KEY_RESIZE":
                self.resize()
        except curses.error:
            return ""
        return key

    def resize(self) -> None:
        curses.update_lines_cols()
        self._window.erase()

        # pylint: disable=no-member
        self.document_view.set_size(curses.LINES - 2, curses.COLS)
        self.status_line_view.move(curses.LINES - 2, 0)
        self.command_line_view.move(curses.LINES - 1, 0)
