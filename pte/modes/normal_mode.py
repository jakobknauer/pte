from pte.text_buffer import TextBuffer
from pte.cursor import Cursor
from pte.view import MainView, colors

from .mode import Mode
from .transition import Transition, TransitionType


class NormalMode(Mode):
    def __init__(self, text_buffer: TextBuffer, cursor: Cursor, view: MainView) -> None:
        super().__init__(name="NORMAL MODE")
        self._text_buffer = text_buffer
        self._cursor = cursor
        self._view = view
        self._view.text_buffer_view.set_text_buffer(self._text_buffer)
        self._command_buffer = _CommandBuffer()
        self._command_executor = _CommandExecutor(text_buffer, cursor)

    def enter(self) -> None:
        self._view.text_buffer_view.status = self.name
        self._view.text_buffer_view.status_color = colors.CYAN
        self._cursor.allow_extra_column = False

    def leave(self) -> None:
        self._view.text_buffer_view.status = f"LEFT {self.name}"
        self._command_buffer.clear()

    def draw(self) -> None:
        self._view.text_buffer_view.set_cursor(self._cursor.line, self._cursor.column)
        self._view.text_buffer_view.consolidate_view_parameters()
        self._view.draw(bottom_line_right=str(self._command_buffer))

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
            len(self.store) <= len(command)
            and command[: len(self.store)] == tuple(self.store)
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
    def __init__(self, text_buffer: TextBuffer, cursor: Cursor):
        self._text_buffer = text_buffer
        self._cursor = cursor

    def execute(self, command: list[str]) -> Transition:
        cursor = self._cursor
        text_buffer = self._text_buffer

        match tuple(command):
            case ("h",):
                cursor.move_left()
                return TransitionType.STAY
            case ("j",):
                cursor.move_down()
                return TransitionType.STAY
            case ("k",):
                cursor.move_up()
                return TransitionType.STAY
            case ("l",):
                cursor.move_right()
                return TransitionType.STAY
            case ("H",):
                cursor.column = 0
                return TransitionType.STAY
            case ("J",):
                cursor.line = -1
                return TransitionType.STAY
            case ("K",):
                cursor.line = 0
                return TransitionType.STAY
            case ("L",):
                cursor.column = -1
                return TransitionType.STAY
            case ("x",):
                line = cursor.line
                column = cursor.column
                text_buffer.delete_in_line(
                    line_number=cursor.line, column_number=column
                )
                if column >= len(text_buffer.get_line(line)):
                    cursor.move_left()
                return TransitionType.STAY
            case ("X",):
                line = cursor.line
                column = cursor.column
                if column > 0:
                    text_buffer.delete_in_line(
                        line_number=line, column_number=column - 1
                    )
                    cursor.move_left()
                return TransitionType.STAY
            case ("d", "d"):
                line = cursor.line
                text_buffer.delete_line(line)
                if line >= text_buffer.number_of_lines():
                    cursor.move_up()
                cursor.column = 0
                return TransitionType.STAY
            case ("i",):
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("a",):
                cursor.allow_extra_column = True
                cursor.move_right()
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("I",):
                cursor.column = 0
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("A",):
                cursor.allow_extra_column = True
                cursor.column = -1
                cursor.move_right()
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("o",):
                line_number = cursor.line + 1
                text_buffer.insert_line(line_number)
                cursor.set(line=line_number, column=0)
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("O",):
                line_number = cursor.line
                text_buffer.insert_line(line_number)
                cursor.set(line=line_number, column=0)
                return (TransitionType.SWITCH, "INSERT MODE")
            case (":",):
                return (TransitionType.SWITCH, "COMMAND MODE")
            case ("Z", "Z"):
                return TransitionType.QUIT
            case ("Z", "Q"):
                return TransitionType.QUIT
            case _:
                raise ValueError(f"Unknown command: {command}.")
