from pte.text_buffer import TextBuffer
from pte.view import MainView, colors

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
ENTER = ["KEY_ENTER", "\n", "\r"]


class CommandMode(Mode):
    def __init__(self, text_buffer: TextBuffer, view: MainView):
        super().__init__(name="COMMAND MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._command_buffer: list[str] = []

    def enter(self) -> None:
        self._view.text_buffer_view.status = self.name
        self._view.text_buffer_view.status_color = colors.YELLOW
        self._view.command_line_view.command = ""
        self._view.command_line_view.active = True

    def leave(self) -> None:
        self._view.text_buffer_view.status = f"LEFT {self.name}"
        self._view.command_line_view.active = False
        self._view.command_line_view.clear()

    def draw(self) -> None:
        self._view.command_line_view.command = "".join(self._command_buffer)
        self._view.draw()

    def update(self) -> Transition:
        self._command_buffer.append(self._view.read())

        match self._command_buffer:
            case [*_, c] if c == ESCAPE:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case [*_, c] if c in ENTER:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case _:
                return TransitionType.STAY
