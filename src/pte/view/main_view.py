import curses

from pte import colors
from pte.highlight import Highlight

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

        self._document_view = DocumentView(document_window)
        self._status_line_view = StatusLineView(status_line_window)
        self._command_line_view = CommandLineView(command_line_window)

    def draw(self, *, show_cursor: bool = True, bottom_line_right: str = "") -> None:
        self._window.noutrefresh()
        self._status_line_view.draw(bottom_line_right=bottom_line_right)
        self._document_view.draw()
        self._command_line_view.draw()

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
        self._document_view.set_size(curses.LINES - 2, curses.COLS)
        self._status_line_view.move(curses.LINES - 2, 0)
        self._command_line_view.move(curses.LINES - 1, 0)

    @property
    def document(self) -> list[str] | None:
        return self._document_view.document

    @document.setter
    def document(self, lines: list[str]) -> None:
        self._document_view.document = lines

    @property
    def highlights(self) -> list[list[Highlight]] | None:
        return self._document_view.highlights

    @highlights.setter
    def highlights(self, highlights: list[list[Highlight]]) -> None:
        self._document_view.highlights = highlights

    @property
    def cursor(self) -> tuple[int, int]:
        return self._document_view.cursor

    @cursor.setter
    def cursor(self, coordinates: tuple[int, int]) -> None:
        self._document_view.cursor = coordinates

    @property
    def status(self) -> str:
        return self._status_line_view.status

    @status.setter
    def status(self, status: str) -> None:
        self._status_line_view.status = status

    @property
    def status_color(self) -> colors.Color:
        return self._status_line_view.status_color

    @status_color.setter
    def status_color(self, status_color: colors.Color) -> None:
        self._status_line_view.status_color = status_color

    @property
    def command(self) -> str:
        return self._command_line_view.command

    @command.setter
    def command(self, command: str) -> None:
        self._command_line_view.command = command

    @property
    def show_command_line(self) -> bool:
        return self._command_line_view.active

    @show_command_line.setter
    def show_command_line(self, do_show: bool) -> None:
        if self._command_line_view.active and not do_show:
            self._command_line_view.clear()
        self._command_line_view.active = do_show
