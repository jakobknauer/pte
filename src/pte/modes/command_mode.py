from pathlib import Path
import re
import string

from pte import colors
from pte.document_buffer import DocumentBuffer
from pte.document_buffer_manager import DocumentBufferManager
from pte.syntax_highlighting import NoOpHighlighter, SyntaxHighlighter
from pte.syntax_highlighting.regex_highlighter import RegexHighlighter
from pte.view import MainView

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
ENTER = ["KEY_ENTER", "\n", "\r"]
BACKSPACE = "KEY_BACKSPACE"
CTRL_R = "\x12"


class CommandMode(Mode):
    def __init__(self, document_buffer_manager: DocumentBufferManager, view: MainView):
        super().__init__(name="COMMAND MODE")
        self._document_buffer_manager = document_buffer_manager
        self._view = view
        self._command_buffer: list[str] = []
        self._command_previewer: _CommandPreviewer = _CommandPreviewer(document_buffer_manager)
        self._command_executor: _CommandExecutor = _CommandExecutor(document_buffer_manager)

    def enter(self, *, command: object = "", **_: object) -> None:
        assert isinstance(command, str)
        self._command_buffer = list(command)

        self._command_previewer.reset()

        self._view.status = self.name
        self._view.status_color = colors.YELLOW
        self._view.command = ""
        self._view.show_command_line = True

    def leave(self) -> None:
        self._view.status = f"LEFT {self.name}"
        self._view.show_command_line = False

    def draw(self) -> None:
        self._view.command = "".join(self._command_buffer)

        if self._document_buffer_manager.active_buffer:
            number_of_lines = self._document_buffer_manager.active_buffer.document.number_of_lines()
            syntax_highlighter = self._document_buffer_manager.active_buffer.highlighter
            search_highlighter = self._command_previewer.highlighter
            self._view.highlights = [
                syntax_highlighter.get_highlights(line) + search_highlighter.get_highlights(line)
                for line in range(number_of_lines)
            ]

        self._view.draw()

    def update(self) -> Transition:
        match self._view.read():
            case "":
                return TransitionType.STAY

            case str(c) if c == ESCAPE:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")

            case str(c) if c in ENTER:
                transition = self._command_executor.execute(self._command_buffer)
                self._command_buffer.clear()
                return transition

            case str(c) if c == BACKSPACE:
                if self._command_buffer:
                    del self._command_buffer[-1]
                    self._command_previewer.update(self._command_buffer)
                    return TransitionType.STAY
                else:
                    return (TransitionType.SWITCH, "NORMAL MODE")

            case str(c) if c in string.printable:
                self._command_buffer.append(c)
                self._command_previewer.update(self._command_buffer)
                return TransitionType.STAY

            case str(s) if s == CTRL_R:
                parts = "".join(self._command_buffer).split()
                if len(parts) > 0 and parts[0] == "search":
                    parts[0] = "replace"
                    self._command_buffer = list(" ".join(parts))
                    self._command_previewer.update(self._command_buffer)
                    return TransitionType.STAY
                return (TransitionType.SWITCH, "NORMAL MODE")

            case _:
                self._command_buffer.clear()
                return (TransitionType.SWITCH, "NORMAL MODE")


class _CommandPreviewer:
    def __init__(self, document_buffer_manager: DocumentBufferManager) -> None:
        self._document_buffer_manager = document_buffer_manager
        self.highlighter: SyntaxHighlighter = NoOpHighlighter()

    def update(self, command: list[str]) -> None:
        active_buffer = self._document_buffer_manager.active_buffer
        parts = "".join(command).split()

        match parts:
            case ["search", str(pattern)] | ["replace", str(pattern)] | [
                "replace",
                str(pattern),
                _,
            ] if active_buffer:
                self.highlighter = RegexHighlighter(active_buffer, pattern)
                self.highlighter.update()

            case _:
                self.reset()

    def reset(self) -> None:
        self.highlighter = NoOpHighlighter()


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

            case ["search", str(pattern)] if active_buffer:
                self._move_to_next_match(active_buffer, pattern)
                return (TransitionType.SWITCH, "NORMAL MODE")

            case ["replace", str(pattern), str(substitute)] if active_buffer:
                active_buffer.document.replace(pattern, substitute)
                return (TransitionType.SWITCH, "NORMAL MODE")

            case _:
                return (TransitionType.SWITCH, "NORMAL MODE")

    def _move_to_next_match(self, buffer: DocumentBuffer, pattern: str) -> None:
        try:
            compiled_pattern = re.compile(pattern)
        except re.error:
            return

        document = buffer.document
        cursor = buffer.cursor

        cursor_position = document.get_index(cursor.line, cursor.column)
        next_match = compiled_pattern.search(document.text, cursor_position + 1)
        if not next_match:
            return

        next_match_index = next_match.start()
        cursor.set(*document.get_coordinates(next_match_index))
