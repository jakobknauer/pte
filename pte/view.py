import curses

from pte.text_buffer import TextBuffer


class View:
    def __init__(self, stdscr: curses.window) -> None:
        self._stdscr = stdscr

        self._text_buffer: TextBuffer | None
        self._visible_lines: tuple[int, int] = (0, 0)
        self._line: int = 0
        self._column: int = 0

        self._bottom_line_index: int = 0

    def set_text_buffer(self, text_buffer: TextBuffer) -> None:
        self._text_buffer = text_buffer

        self._line = 0

        screen_height, _ = self._stdscr.getmaxyx()
        buffer_size = text_buffer.number_of_lines()

        self._visible_lines = (0, min(screen_height - 2, buffer_size))

        self._bottom_line_index = screen_height - 1

    def draw(self, *, bottom_line_left: str = "", bottom_line_right: str = "") -> None:
        if self._stdscr is None:
            return

        self._stdscr.erase()

        if self._text_buffer is None:
            return

        first, last = self._visible_lines
        for screen_line_number, buffer_line_number in zip(
            range(last - first), range(first, last)
        ):
            line = self._text_buffer.get_line(buffer_line_number)
            self._stdscr.addstr(screen_line_number, 0, line)

        self._stdscr.addstr(
            self._bottom_line_index,
            0,
            f" {bottom_line_left} ",
            curses.color_pair(7) ^ curses.A_REVERSE ^ curses.A_BOLD,
        )
        self._stdscr.addstr(
            self._bottom_line_index,
            self.get_screen_width() - 1 - len(bottom_line_right),
            bottom_line_right,
        )

        self._stdscr.noutrefresh()
        curses.setsyx(self._line, self._column)
        curses.doupdate()

    def move_up(self, lines=1) -> None:
        self.set_cursor(self._line - lines, self._column)

    def move_down(self, lines=1) -> None:
        self.set_cursor(self._line + lines, self._column)

    def move_left(self, columns=1) -> None:
        self.set_cursor(self._line, max(0, self._column - columns))

    def move_right(self, columns=1) -> None:
        self.set_cursor(self._line, self._column + columns)

    def set_column(self, column) -> None:
        self.set_cursor(self._line, column)

    def set_cursor(self, line, column) -> None:
        if self._text_buffer is None:
            return

        line = max(0, min(self._text_buffer.number_of_lines() - 1, line))
        self._line = line

        first, last = self._visible_lines
        if self._line >= last:
            overflow = self._line - last + 1
            self._visible_lines = (first + overflow, last + overflow)
        elif self._line < first:
            overflow = first - self._line
            self._visible_lines = (first - overflow, last - overflow)

        if column < 0:
            column = len(self._text_buffer.get_line(self._line)) - 1 - column

        self._column = max(
            0, min(column, len(self._text_buffer.get_line(self._line)) - 1)
        )

    def get_column(self) -> int:
        return self._column

    def get_line(self) -> int:
        return self._line

    def get_screen_width(self) -> int:
        return self._stdscr.getmaxyx()[1]
