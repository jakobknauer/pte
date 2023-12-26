import string

from pte.text_buffer import TextBuffer
from pte.view import MainView
from pte.command_buffer import CommandBuffer

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
DEL = "KEY_DC"
BACKSPACE = "KEY_BACKSPACE"


class InsertMode(Mode):
    def __init__(
        self, text_buffer: TextBuffer, view: MainView, command_buffer: CommandBuffer
    ):
        super().__init__(name="INSERT MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._command_buffer: CommandBuffer = command_buffer

    def enter(self) -> None:
        ...

    def leave(self) -> None:
        self._command_buffer.clear()

    def draw(self) -> None:
        self._view.draw(
            bottom_line_left=self.name,
            bottom_line_right=str(self._command_buffer.get_store()),
        )

    def update(self) -> Transition:
        self._command_buffer.read()
        command = self._command_buffer.get_store()
        text_buffer_view = self._view.text_buffer_view

        match command:
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
