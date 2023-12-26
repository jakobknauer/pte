from pte.state import State
from pte.text_buffer import TextBuffer
from pte.view import MainView
from pte.command_buffer import CommandBuffer


ESCAPE = "\x1b"
ENTER = ["KEY_ENTER", "\n", "\r"]


class CommandMode(State):
    def __init__(
        self, text_buffer: TextBuffer, view: MainView, command_buffer: CommandBuffer
    ):
        super().__init__(name="COMMAND MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._command_buffer: CommandBuffer = command_buffer

        self._normal_mode: State

    def draw(self) -> None:
        self._view.command_line_view.command = "".join(self._command_buffer.get_store())
        self._view.command_line_view.active = True

        self._view.draw(bottom_line_left=self._name)

    def update(self) -> State | None:
        self._command_buffer.read()
        command = self._command_buffer.get_store()

        match command:
            case [*_, c] if c == ESCAPE:
                self._command_buffer.clear()
                return self._normal_mode
            case [*_, c] if c in ENTER:
                self._command_buffer.clear()
                return self._normal_mode
            case _:
                return self

    def set_normal_mode(self, normal_mode: State) -> None:
        self._normal_mode = normal_mode
