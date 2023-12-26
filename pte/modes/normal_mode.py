from pte.text_buffer import TextBuffer
from pte.view import MainView
from pte.command_buffer import CommandBuffer

from .mode import Mode
from .transition import Transition, TransitionType


class NormalMode(Mode):
    def __init__(
        self, text_buffer: TextBuffer, view: MainView, command_buffer: CommandBuffer
    ):
        super().__init__(name="NORMAL MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._view.text_buffer_view.set_text_buffer(self._text_buffer)
        self._command_buffer = command_buffer

    def enter(self) -> None:
        self._view.text_buffer_view.status = self.name

    def leave(self) -> None:
        self._view.text_buffer_view.status = f"LEFT {self.name}"
        self._command_buffer.clear()

    def draw(self) -> None:
        self._view.draw(
            bottom_line_right="".join(self._command_buffer.get_store()),
        )

    def update(self) -> Transition:
        self._command_buffer.read()
        text_buffer_view = self._view.text_buffer_view

        match self._command_buffer.get_store():
            case ["q"]:
                return None
            case ["k"]:
                text_buffer_view.move_up()
                self._command_buffer.clear()
                return TransitionType.STAY
            case ["j"]:
                text_buffer_view.move_down()
                self._command_buffer.clear()
                return TransitionType.STAY
            case ["h"]:
                text_buffer_view.move_left()
                self._command_buffer.clear()
                return TransitionType.STAY
            case ["l"]:
                text_buffer_view.move_right()
                self._command_buffer.clear()
                return TransitionType.STAY
            case ["0"]:
                text_buffer_view.set_column(0)
                self._command_buffer.clear()
                return TransitionType.STAY
            case ["$"]:
                text_buffer_view.set_column(-1)
                self._command_buffer.clear()
                return TransitionType.STAY
            case ["i"]:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "INSERT MODE")
            case [":"]:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "COMMAND MODE")
            case ["Z", "Z"]:
                return TransitionType.QUIT
            case ["Z"]:
                return TransitionType.STAY
            case _:
                self._command_buffer.clear()
                return TransitionType.STAY
