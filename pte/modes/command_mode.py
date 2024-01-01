import string
from pathlib import Path

from pte.text_buffer_manager import TextBufferManager
from pte.view import MainView, colors

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
ENTER = ["KEY_ENTER", "\n", "\r"]
BACKSPACE = "KEY_BACKSPACE"


class CommandMode(Mode):
    def __init__(self, text_buffer_manager: TextBufferManager, view: MainView):
        super().__init__(name="COMMAND MODE")
        self._text_buffer_manager = text_buffer_manager
        self._view = view
        self._command_buffer: list[str] = []
        self._command_executor: _CommandExecutor = _CommandExecutor(text_buffer_manager)

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
        match self._view.read():
            case "":
                return TransitionType.STAY
            case c if c == ESCAPE:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case c if c in ENTER:
                transition = self._command_executor.execute(self._command_buffer)
                self._command_buffer.clear()
                return transition
            case c if c == BACKSPACE:
                if self._command_buffer:
                    del self._command_buffer[-1]
                    return TransitionType.STAY
                else:
                    return (TransitionType.SWITCH, "NORMAL MODE")
            case c if c in string.printable:
                self._command_buffer.append(c)
                return TransitionType.STAY
            case _:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")


class _CommandExecutor:
    def __init__(self, text_buffer_manager: TextBufferManager) -> None:
        self._text_buffer_manager = text_buffer_manager

    def execute(self, command: list[str]) -> Transition:
        active_buffer = self._text_buffer_manager.active_buffer
        parts = "".join(command).split()

        match parts:
            case ["save", str(path)] if active_buffer:
                self._text_buffer_manager.save_buffer(Path(path))
                return (TransitionType.SWITCH, "NORMAL MODE")
            case ["save"] if active_buffer:
                self._text_buffer_manager.save_buffer()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case ["load", str(path)]:
                self._text_buffer_manager.load_file(Path(path))
                return (TransitionType.SWITCH, "NORMAL MODE")
            case ["quit"]:
                return TransitionType.QUIT
            case ["empty"]:
                self._text_buffer_manager.load_empty_buffer()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case _:
                return (TransitionType.SWITCH, "NORMAL MODE")
