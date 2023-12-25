from pte.state import State
from pte.text_buffer import TextBuffer
from pte.view import View
from pte.command_buffer import CommandBuffer


class InsertMode(State):
    def __init__(self, text_buffer: TextBuffer, view: View, command_buffer: CommandBuffer):
        super().__init__(name="INSERT MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._view.set_text_buffer(self._text_buffer)
        self._command_buffer = command_buffer

    def draw(self) -> None:
        self._view.draw(self._name)

    def update(self) -> State | None:
        self._command_buffer.read()
        return self
