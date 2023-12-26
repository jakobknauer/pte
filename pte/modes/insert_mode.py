import string

from pte.text_buffer import TextBuffer
from pte.view import MainView

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
DEL = "KEY_DC"
BACKSPACE = "KEY_BACKSPACE"


class InsertMode(Mode):
    def __init__(self, text_buffer: TextBuffer, view: MainView):
        super().__init__(name="INSERT MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._command_buffer: list[str] = []

    def enter(self) -> None:
        self._view.text_buffer_view.status = self.name

    def leave(self) -> None:
        self._view.text_buffer_view.status = f"LEFT {self.name}"
        self._command_buffer.clear()

    def draw(self) -> None:
        self._view.draw()

    def update(self) -> Transition:
        self._command_buffer.append(self._view.read())
        text_buffer_view = self._view.text_buffer_view

        match self._command_buffer:
            case [c] if c == ESCAPE:
                self._command_buffer.clear()
                text_buffer_view.move_left()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case [str(c)] if len(c) == 1 and c in string.printable:
                self._command_buffer.clear()
                self._text_buffer.insert(
                    line_number=text_buffer_view.get_line(),
                    column_number=text_buffer_view.get_column(),
                    text=c,
                )
                text_buffer_view.move_right(1)
                return TransitionType.STAY
            case [c] if c == DEL:
                self._command_buffer.clear()
                self._text_buffer.delete_in_line(
                    line_number=text_buffer_view.get_line(),
                    column_number=text_buffer_view.get_column(),
                )
                return TransitionType.STAY
            case [c] if c == BACKSPACE:
                self._command_buffer.clear()
                self._text_buffer.delete_in_line(
                    line_number=text_buffer_view.get_line(),
                    column_number=text_buffer_view.get_column() - 1,
                )
                text_buffer_view.move_left(1)
                return TransitionType.STAY
            case _:
                self._command_buffer.clear()
                return TransitionType.STAY
