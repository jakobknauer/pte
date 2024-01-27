from pte import colors
from pte.document_buffer import DocumentBuffer
from pte.document_buffer_manager import DocumentBufferManager
from pte.view import MainView

from .mode import Mode
from .transition import Transition, TransitionType


class NormalMode(Mode):
    def __init__(self, document_buffer_manager: DocumentBufferManager, view: MainView) -> None:
        super().__init__(name="NORMAL MODE")
        self._document_buffer_manager = document_buffer_manager
        self._view = view
        self._command_buffer = _CommandBuffer()
        self._command_executor = _CommandExecutor(document_buffer_manager)

        self._document_buffer: DocumentBuffer | None = None

    def enter(self) -> None:
        if self._document_buffer_manager.active_buffer:
            self._document_buffer = self._document_buffer_manager.active_buffer
            self._document_buffer.cursor.allow_extra_column = False
            self._document_buffer.highlighter.update()

        self._view.document_view.status = self.name
        self._view.document_view.status_color = colors.CYAN

    def leave(self) -> None:
        self._view.document_view.status = f"LEFT {self.name}"
        self._command_buffer.clear()

    def draw(self) -> None:
        if self._document_buffer:
            self._view.document_view.document = list(self._document_buffer.document)
            self._view.document_view.set_cursor(
                self._document_buffer.cursor.line, self._document_buffer.cursor.column
            )
            self._view.document_view.consolidate_view_parameters()

            self._view.document_view.highlights = [
                self._document_buffer.highlighter.get_highlights(line)
                for line in range(self._document_buffer.document.number_of_lines())
            ]

            self._view.draw(bottom_line_right=str(self._command_buffer))
        else:
            self._view.draw(bottom_line_right="[no buffer]", show_cursor=False)

    def update(self) -> Transition:
        self._command_buffer.append(self._view.read())

        if self._command_buffer.is_command():
            transition = self._command_executor.execute(self._command_buffer.store)
            self._command_buffer.clear()
            return transition
        elif not self._command_buffer.is_prefix():
            self._command_buffer.clear()

        return TransitionType.STAY


_COMMANDS = {
    # movement
    ("h",),
    ("j",),
    ("k",),
    ("l",),
    ("H",),
    ("J",),
    ("K",),
    ("L",),
    # deletion
    ("x",),
    ("X",),
    ("d", "d"),
    # switch to insert mode
    ("i",),
    ("a",),
    ("I",),
    ("A",),
    ("o",),
    ("O",),
    # switch to command mode
    (":",),
    # quitting
    ("Z", "Z"),
    ("Z", "Q"),
}


class _CommandBuffer:
    def __init__(self) -> None:
        self.store: list[str] = []

    def is_command(self) -> bool:
        return tuple(self.store) in _COMMANDS

    def is_prefix(self) -> bool:
        return any(
            len(self.store) <= len(command) and command[: len(self.store)] == tuple(self.store)
            for command in _COMMANDS
        )

    def append(self, key: str) -> None:
        if key != "":
            self.store.append(key)

    def clear(self) -> None:
        self.store.clear()

    def __str__(self) -> str:
        return "".join(self.store)


class _CommandExecutor:
    def __init__(self, document_buffer_manager: DocumentBufferManager):
        self._document_buffer_manager = document_buffer_manager

    def execute(self, command: list[str]) -> Transition:
        active_buffer = self._document_buffer_manager.active_buffer
        if active_buffer:
            document = active_buffer.document
            cursor = active_buffer.cursor

        match tuple(command):
            case ("h",) if active_buffer:
                cursor.move_left()
                return TransitionType.STAY
            case ("j",) if active_buffer:
                cursor.move_down()
                return TransitionType.STAY
            case ("k",) if active_buffer:
                cursor.move_up()
                return TransitionType.STAY
            case ("l",) if active_buffer:
                cursor.move_right()
                return TransitionType.STAY
            case ("H",) if active_buffer:
                cursor.column = 0
                return TransitionType.STAY
            case ("J",) if active_buffer:
                cursor.line = cursor.max_line
                return TransitionType.STAY
            case ("K",) if active_buffer:
                cursor.line = 0
                return TransitionType.STAY
            case ("L",) if active_buffer:
                cursor.column = cursor.max_column
                return TransitionType.STAY
            case ("x",) if active_buffer and not document.is_empty:
                line = cursor.line
                column = cursor.column
                document.delete_in_line(line_number=cursor.line, column_number=column)
                if column >= document.get_line_length(line):
                    cursor.move_left()
                return TransitionType.STAY
            case ("X",) if active_buffer and not document.is_empty:
                line = cursor.line
                column = cursor.column
                if column > 0:
                    document.delete_in_line(line_number=line, column_number=column - 1)
                    cursor.move_left()
                return TransitionType.STAY
            case ("d", "d") if active_buffer and not document.is_empty:
                line = cursor.line
                document.delete_line(line)
                if line >= document.number_of_lines():
                    cursor.move_up()
                cursor.column = 0
                return TransitionType.STAY
            case ("i",) if active_buffer:
                if document.is_empty:
                    document.insert_line(0)
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("a",) if active_buffer:
                if document.is_empty:
                    document.insert_line(0)
                cursor.allow_extra_column = True
                cursor.move_right()
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("I",) if active_buffer:
                if document.is_empty:
                    document.insert_line(0)
                cursor.column = 0
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("A",) if active_buffer:
                if document.is_empty:
                    document.insert_line(0)
                cursor.allow_extra_column = True
                cursor.column = document.get_line_length(cursor.line)
                cursor.move_right()
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("o",) if active_buffer:
                line_number = cursor.line + 1
                document.insert_line(line_number)
                cursor.set(line=line_number, column=0)
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("O",) if active_buffer:
                line_number = cursor.line
                document.insert_line(line_number)
                cursor.set(line=line_number, column=0)
                return (TransitionType.SWITCH, "INSERT MODE")
            case (":",):
                return (TransitionType.SWITCH, "COMMAND MODE")
            case ("Z", "Z"):
                if active_buffer:
                    self._document_buffer_manager.save_buffer()
                return TransitionType.QUIT
            case ("Z", "Q"):
                return TransitionType.QUIT
            case cmd if cmd in _COMMANDS:
                return TransitionType.STAY
            case _:
                raise ValueError(f"Unknown command: {command}.")
