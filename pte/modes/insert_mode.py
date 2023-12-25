import string

from pte.state import State
from pte.text_buffer import TextBuffer
from pte.view import View
from pte.command_buffer import CommandBuffer


ESCAPE = "\x1b"
DEL = "KEY_DC"
BACKSPACE = "KEY_BACKSPACE"


class InsertMode(State):
    def __init__(
        self, text_buffer: TextBuffer, view: View, command_buffer: CommandBuffer
    ):
        super().__init__(name="INSERT MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._view.set_text_buffer(self._text_buffer)
        self._command_buffer: CommandBuffer = command_buffer

        self._normal_mode: State | None = None

    def draw(self) -> None:
        self._view.draw(
            bottom_line_left=self._name,
            bottom_line_right=str(self._command_buffer.get_store()),
        )

    def update(self) -> State | None:
        self._command_buffer.read()
        command = self._command_buffer.get_store()

        match command:
            case [c] if c == ESCAPE:
                self._command_buffer.clear()
                self._view.move_left()
                return self._normal_mode
            case [str(c)] if len(c) == 1 and c in string.printable:
                self._command_buffer.clear()
                self._text_buffer.insert(
                    line_number=self._view.get_line(),
                    column_number=self._view.get_column(),
                    text=c,
                )
                self._view.move_right(1)
                return self
            case [c] if c == DEL:
                self._command_buffer.clear()
                self._text_buffer.delete_in_line(
                    line_number=self._view.get_line(),
                    column_number=self._view.get_column(),
                )
                return self
            case [c] if c == BACKSPACE:
                self._command_buffer.clear()
                self._text_buffer.delete_in_line(
                    line_number=self._view.get_line(),
                    column_number=self._view.get_column() - 1,
                )
                self._view.move_left(1)
                return self
            case _:
                self._command_buffer.clear()
                return self

    def set_normal_mode(self, normal_mode: State) -> None:
        self._normal_mode = normal_mode
