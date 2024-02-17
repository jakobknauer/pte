import curses
import logging

from pte.highlight import Highlight


log = logging.getLogger(__name__)


class DocumentView:
    def __init__(self, window: curses.window) -> None:
        # curses stuff
        self._window = window

        # view content
        self.document: list[str] | None = None
        self.highlights: list[list[Highlight]] = []

        # the part of the buffer currently visible on screen, represented by the number of the
        # first visible line, and the the number of the first non-visible line below that.
        self._buffer_window: tuple[int, int] = (0, 0)

        # cursor position
        self._line: int = 0
        self._column: int = 0

    @property
    def cursor(self) -> tuple[int, int]:
        return (self._line, self._column)

    @cursor.setter
    def cursor(self, coordinates: tuple[int, int]) -> None:
        self._line, self._column = coordinates

    @property
    def window_height(self) -> int:
        return self._window.getmaxyx()[0]

    @property
    def window_width(self) -> int:
        return self._window.getmaxyx()[1]

    def set_size(self, height: int, width: int) -> None:
        self._window.resize(height, width)
        self._consolidate_view_parameters()

    def draw(self) -> None:
        self._consolidate_view_parameters()
        self._window.erase()
        self._draw_document()

    def _draw_document(self) -> None:
        if self.document is None:
            return

        first, last = self._buffer_window

        for screen_line_number, buffer_line_number in zip(range(last - first), range(first, last)):
            line = self.document[buffer_line_number]
            self._window.addstr(screen_line_number, 0, line)

            line_hls = self.highlights[buffer_line_number] if self.highlights else []
            for hl in line_hls:
                self._window.addstr(
                    screen_line_number,
                    hl.column,
                    line[hl.column : hl.column + hl.length],
                    curses.color_pair(hl.color),
                )

        self._window.noutrefresh()
        curses.setsyx(self._line - self._buffer_window[0], self._column)

    def _consolidate_view_parameters(self) -> None:
        """Ensures the consistency of the view parameters with relevant environment parameters.

        The view parameters encompasses the buffer window.
        The relevant environment parameters encompass the document, cursor, and screen size.

        Should be called whenever one of the following has changed:
            - _window, or its size
            - _document, or its size
            - the cursor position (more specifically, _line)

        If the cursor is outside of the buffer window, move the buffer window until it contains
        the cursor.

        If the screen height increased, grow the buffer window as far to the bottom as possible;
        then, if the end of the text buffer is reached, grow the buffer window as far to the top as
        possible.

        If the screen height decreased, shrink the buffer window from the bottom upwards towards
        the cursor as far as possible; then, if needed, from the top downwards towards the cursor.
        """
        if not self.document:
            self._line = 0
            self._column = 0
            self._buffer_window = (0, 0)
            return

        buffer_window_top, buffer_window_bottom = self._buffer_window
        buffer_window_height = buffer_window_bottom - buffer_window_top

        # shrink buffer window it goes beyond the end of the buffer
        buffer_window_bottom = min(buffer_window_bottom, len(self.document))

        # grow buffer window if possible, shrink buffer window if needed
        available_screen_height = self.window_height
        if buffer_window_height <= available_screen_height:
            # move bottom as far down as possible
            buffer_window_bottom = min(
                len(self.document), buffer_window_top + available_screen_height
            )
            buffer_window_height = buffer_window_bottom - buffer_window_top
            assert 0 <= buffer_window_height <= available_screen_height

            # move top as far up as possible
            if buffer_window_height < available_screen_height:
                buffer_window_top = max(0, buffer_window_bottom - available_screen_height)

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

        # move buffer window to ensure it contains the cursor
        if self._line >= buffer_window_bottom:
            overflow = self._line - buffer_window_bottom + 1
            buffer_window_top += overflow
            buffer_window_bottom += overflow
        elif self._line < buffer_window_top:
            overflow = buffer_window_top - self._line
            buffer_window_top -= overflow
            buffer_window_bottom -= overflow

        self._buffer_window = (buffer_window_top, buffer_window_bottom)
        self._assert_view_parameters_consistency()

    def _assert_view_parameters_consistency(self) -> None:
        assert self.document is not None

        buffer_window_top, buffer_window_bottom = self._buffer_window
        buffer_window_height = buffer_window_bottom - buffer_window_top

        available_screen_height = self.window_height

        assert 0 <= buffer_window_height <= available_screen_height
        assert 0 <= buffer_window_top <= self._line < buffer_window_bottom <= len(self.document)
