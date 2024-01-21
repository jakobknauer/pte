import string
from pathlib import Path

from pte import colors
from pte.document_buffer_manager import DocumentBufferManager
from pte.view import MainView

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
ENTER = ["KEY_ENTER", "\n", "\r"]
BACKSPACE = "KEY_BACKSPACE"


class CommandMode(Mode):
    def __init__(self, document_buffer_manager: DocumentBufferManager, view: MainView):
        super().__init__(name="COMMAND MODE")
        self._document_buffer_manager = document_buffer_manager
        self._view = view
        self._command_buffer: list[str] = []
        self._command_executor: _CommandExecutor = _CommandExecutor(document_buffer_manager)

    def enter(self) -> None:
        self._view.document_view.status = self.name
        self._view.document_view.status_color = colors.YELLOW
        self._view.command_line_view.command = ""
        self._view.command_line_view.active = True

    def leave(self) -> None:
        self._view.document_view.status = f"LEFT {self.name}"
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
    def __init__(self, document_buffer_manager: DocumentBufferManager) -> None:
        self._document_buffer_manager = document_buffer_manager

    def execute(self, command: list[str]) -> Transition:
        active_buffer = self._document_buffer_manager.active_buffer
        parts = "".join(command).split()

        match parts:
            case ["save", str(path)] if active_buffer:
                self._document_buffer_manager.save_buffer(Path(path))
                return (TransitionType.SWITCH, "NORMAL MODE")
            case ["save"] if active_buffer:
                self._document_buffer_manager.save_buffer()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case ["load", str(path)]:
                self._document_buffer_manager.load_file(Path(path))
                return (TransitionType.SWITCH, "NORMAL MODE")
            case ["quit"]:
                return TransitionType.QUIT
            case ["empty"]:
                self._document_buffer_manager.load_empty_buffer()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case _:
                return (TransitionType.SWITCH, "NORMAL MODE")
