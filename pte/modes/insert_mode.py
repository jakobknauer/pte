import curses.ascii

from pte.state import State
from pte.text_buffer import TextBuffer
from pte.view import View
from pte.command_buffer import CommandBuffer


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
        self._view.draw(f"{self._name}\t{self._command_buffer.get_store()}")

    def update(self) -> State | None:
        self._command_buffer.read()
        match self._command_buffer.get_store():
            case ["\x1b"]:
                self._command_buffer.clear()
                return self._normal_mode
            case _:
                self._command_buffer.clear()
                return self

    def set_normal_mode(self, normal_mode: State) -> None:
        self._normal_mode = normal_mode
