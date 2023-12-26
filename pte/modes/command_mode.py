from pte.text_buffer import TextBuffer
from pte.view import MainView
from pte.command_buffer import CommandBuffer

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
ENTER = ["KEY_ENTER", "\n", "\r"]


class CommandMode(Mode):
    def __init__(
        self, text_buffer: TextBuffer, view: MainView, command_buffer: CommandBuffer
    ):
        super().__init__(name="COMMAND MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._command_buffer: CommandBuffer = command_buffer

    def enter(self) -> None:
        self._view.command_line_view.active = True

    def leave(self) -> None:
        self._view.command_line_view.active = False

    def draw(self) -> None:
        self._view.command_line_view.command = "".join(self._command_buffer.get_store())
        self._view.draw(bottom_line_left=self.name)

    def update(self) -> Transition:
        self._command_buffer.read()
        command = self._command_buffer.get_store()

        match command:
            case [*_, c] if c == ESCAPE:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case [*_, c] if c in ENTER:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case _:
                return TransitionType.STAY
