from pte.state import State
from pte.text_buffer import TextBuffer
from pte.view import View
from pte.command_buffer import CommandBuffer


class NormalMode(State):
    def __init__(self, text_buffer: TextBuffer, view: View, command_buffer: CommandBuffer):
        super().__init__(name="NORMAL MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._view.set_text_buffer(self._text_buffer)
        self._command_buffer = command_buffer

    def draw(self) -> None:
        self._view.draw()

    def update(self) -> State:
        self._command_buffer.read()

        match self._command_buffer.get_store():
            case ["q"]:
                return None
            case ["k"]:
                self._view.move_up()
                self._command_buffer.clear()
                return self
            case ["j"]:
                self._view.move_down()
                self._command_buffer.clear()
                return self
            case ["h"]:
                self._view.move_left()
                self._command_buffer.clear()
                return self
            case ["l"]:
                self._view.move_right()
                self._command_buffer.clear()
                return self
            case ["0"]:
                self._view.set_column(0)
                self._command_buffer.clear()
                return self
            case ["$"]:
                self._view.set_column(-1)
                self._command_buffer.clear()
                return self
            case ["Z","Z"]:
                return None
            case ["Z"]:
                return self
            case _:
                self._command_buffer.clear()
                return self
