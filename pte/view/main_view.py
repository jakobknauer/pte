import curses

from .text_buffer_view import TextBufferView
from .command_line_view import CommandLineView


class MainView:
    def __init__(self, window: curses.window):
        self._window = window

        text_buffer_window = window.derwin(curses.LINES - 1, curses.COLS, 0, 0)
        command_line_window = window.derwin(1, curses.COLS, curses.LINES - 1, 0)

        self.text_buffer_view = TextBufferView(text_buffer_window)
        self.command_line_view = CommandLineView(command_line_window)

    def draw(
        self,
        *,
        bottom_line_left: str = "",
        bottom_line_right: str = "",
    ) -> None:
        self.text_buffer_view.draw(
            bottom_line_left=bottom_line_left, bottom_line_right=bottom_line_right
        )
        self.command_line_view.draw()
