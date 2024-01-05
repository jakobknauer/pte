import curses

from . import colors


STATUS_LINE_HEIGHT = 1


class TextBufferView:
    def __init__(self, window: curses.window) -> None:
        # curses stuff
        self._window = window

        # view content
        self._text_buffer: list[str] | None = None
        self.status: str = ""
        self.status_color: colors.Color = colors.DEFAULT

        # the part of the buffer currently visible on screen, represented by the number of the
        # first visible line, and the the number of the first non-visible line below that.
        self._buffer_window: tuple[int, int]

        # cursor position
        self._line: int = 0
        self._column: int = 0

    def set_text_buffer(self, lines: list[str]) -> None:
        self._text_buffer = lines
        self._buffer_window = (0, 0)
        self._line = 0
        self._column = 0

        self.consolidate_view_parameters()

    def set_size(self, height: int, width: int) -> None:
        self._window.resize(height, width)

        self.consolidate_view_parameters()

    def consolidate_view_parameters(self) -> None:
        """Ensures the consistency of the view parameters with relevant environment parameters.

        The view parameters encompasses the buffer window.
        The relevant environment parameters encompass the text buffer, cursor, and screen size.

        Should be called whenever one of the following has changed:
            - _window, or its size
            - _text_buffer, or its size
            - the cursor position (more specifically, _line)

        If the cursor is outside of the buffer window, move the buffer window until it contains
        the cursor.

        If the screen height increased, grow the buffer window as far to the bottom as possible;
        then, if the end of the text buffer is reached, grow the buffer window as far to the top as
        possible.

        If the screen height decreased, shrink the buffer window from the bottom upwards towards
        the cursor as far as possible; then, if needed, from the top downwards towards the cursor.
        """
        if not self._text_buffer:
            return

        buffer_window_top, buffer_window_bottom = self._buffer_window
        buffer_window_height = buffer_window_bottom - buffer_window_top

        # move buffer window to ensure it contains the cursor
        if self._line >= buffer_window_bottom:
            overflow = self._line - buffer_window_bottom + 1
            buffer_window_top += overflow
            buffer_window_bottom += overflow
        elif self._line < buffer_window_top:
            overflow = buffer_window_top - self._line
            buffer_window_top -= overflow
            buffer_window_bottom -= overflow

        # shrink buffer window it goes beyond the end of the buffer
        buffer_window_bottom = max(buffer_window_bottom, len(self._text_buffer))

        # grow buffer window if possible, shrink buffer window if needed
        available_screen_height = self.get_window_height() - STATUS_LINE_HEIGHT
        if buffer_window_height <= available_screen_height:
            # move bottom as far down as possible
            buffer_window_bottom = min(
                len(self._text_buffer), buffer_window_top + available_screen_height
            )
            buffer_window_height = buffer_window_bottom - buffer_window_top
            assert 0 <= buffer_window_height <= available_screen_height

            # move top as far up as possible
            if buffer_window_height < available_screen_height:
                buffer_window_top = max(
                    0, buffer_window_bottom - available_screen_height
                )

            buffer_window_height = buffer_window_bottom - buffer_window_top
            assert 0 <= buffer_window_height <= available_screen_height
        else:
            # move bottom up as far as needed, but no higher than the cursor
            buffer_window_bottom = max(
                self._line + 1,
                buffer_window_bottom - (buffer_window_height - available_screen_height),
            )
            buffer_window_height = buffer_window_bottom - buffer_window_top
            assert 0 <= buffer_window_height

            # move top down, if needed
            if buffer_window_height > available_screen_height:
                buffer_window_top += buffer_window_height - available_screen_height

            buffer_window_height = buffer_window_bottom - buffer_window_top
            assert 0 <= buffer_window_height <= available_screen_height
            assert buffer_window_top <= self._line < buffer_window_bottom

        self._buffer_window = (buffer_window_top, buffer_window_bottom)
        self._assert_view_parameters_consistency()

    def _assert_view_parameters_consistency(self) -> None:
        assert self._text_buffer is not None

        buffer_window_top, buffer_window_bottom = self._buffer_window
        buffer_window_height = buffer_window_bottom - buffer_window_top

        available_screen_height = self.get_window_height() - STATUS_LINE_HEIGHT

        assert 0 <= buffer_window_height <= available_screen_height
        assert (
            0
            <= buffer_window_top
            <= self._line
            < buffer_window_bottom
            <= len(self._text_buffer)
        )

    def draw(self, *, bottom_line_right: str = "") -> None:
        self._window.erase()

        status_line_number = self.get_window_height() - STATUS_LINE_HEIGHT
        self._window.addstr(
            status_line_number,
            0,
            f" {self.status} ",
            curses.color_pair(self.status_color) ^ curses.A_REVERSE ^ curses.A_BOLD,
        )
        self._window.addstr(
            status_line_number,
            self.get_screen_width() - 1 - len(bottom_line_right),
            bottom_line_right,
        )
        self._window.noutrefresh()

        if self._text_buffer is not None:
            first, last = self._buffer_window
            for screen_line_number, buffer_line_number in zip(
                range(last - first), range(first, last)
            ):
                line = self._text_buffer[buffer_line_number]
                self._window.addstr(screen_line_number, 0, line)

            self._window.noutrefresh()
            curses.setsyx(self._line - self._buffer_window[0], self._column)

    def set_cursor(self, line: int, column: int) -> None:
        self._line = line
        self._column = column

    def get_window_height(self) -> int:
        return self._window.getmaxyx()[0]

    def get_screen_width(self) -> int:
        return self._window.getmaxyx()[1]
