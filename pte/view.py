import curses

from pte.text_buffer import TextBuffer


class View:
    def __init__(self) -> None:
        self._stdscr: curses.window = None  # type: ignore

        self._text_buffer: TextBuffer | None
        self._window: tuple[int, int] = (0, 0)
        self._line: int = 0
        self._column: int = 0

    def __enter__(self):
        self._stdscr = curses.initscr()
        curses.noecho()
        # curses.curs_set(False)
        curses.cbreak()
        self._stdscr.keypad(True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        curses.nocbreak()
        self._stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def set_text_buffer(self, text_buffer: TextBuffer) -> None:
        self._text_buffer = text_buffer

        self._line = 0

        screen_height, _ = self._stdscr.getmaxyx()
        buffer_size = text_buffer.number_of_lines()

        self._window = (0, min(screen_height, buffer_size))

    def draw(self) -> None:
        if self._stdscr is None:
            return

        self._stdscr.erase()

        if self._text_buffer is None:
            return

        first, last = self._window
        for screen_line_number, buffer_line_number in zip(
            range(last - first), range(first, last)
        ):
            self._stdscr.addstr(
                screen_line_number, 0, self._text_buffer.get_line(buffer_line_number)
            )

        self._stdscr.noutrefresh()
        curses.setsyx(self._line, self._column)
        curses.doupdate()


    def input(self) -> str:
        return self._stdscr.getkey()
