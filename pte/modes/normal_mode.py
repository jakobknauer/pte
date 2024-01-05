from pte.text_buffer import TextBuffer
from pte.text_buffer_manager import TextBufferManager
from pte.cursor import Cursor
from pte.view import MainView, colors

from .mode import Mode
from .transition import Transition, TransitionType


class NormalMode(Mode):
    def __init__(self, text_buffer_manager: TextBufferManager, view: MainView) -> None:
        super().__init__(name="NORMAL MODE")
        self._text_buffer_manager = text_buffer_manager
        self._view = view
        self._command_buffer = _CommandBuffer()
        self._command_executor: _CommandExecutor = _CommandExecutor(text_buffer_manager)

        self._text_buffer: TextBuffer | None = None
        self._cursor: Cursor | None = None

    def enter(self) -> None:
        if self._text_buffer_manager.active_buffer:
            self._text_buffer = self._text_buffer_manager.active_buffer[0]
            self._cursor = self._text_buffer_manager.active_buffer[1]

            self._cursor.allow_extra_column = False

        self._view.text_buffer_view.status = self.name
        self._view.text_buffer_view.status_color = colors.CYAN

    def leave(self) -> None:
        self._view.text_buffer_view.status = f"LEFT {self.name}"
        self._command_buffer.clear()

    def draw(self) -> None:
        if self._text_buffer and self._cursor:
            self._view.text_buffer_view.set_text_buffer(list(self._text_buffer))
            self._view.text_buffer_view.set_cursor(
                self._cursor.line, self._cursor.column
            )
            self._view.text_buffer_view.consolidate_view_parameters()
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
    def __init__(self, text_buffer_manager: TextBufferManager):
        self._text_buffer_manager = text_buffer_manager

    def execute(self, command: list[str]) -> Transition:
        active_buffer = self._text_buffer_manager.active_buffer
        if active_buffer:
            text_buffer = active_buffer[0]
            cursor = active_buffer[1]

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
                cursor.line = -1
                return TransitionType.STAY
            case ("K",) if active_buffer:
                cursor.line = 0
                return TransitionType.STAY
            case ("L",) if active_buffer:
                cursor.column = -1
                return TransitionType.STAY
            case ("x",) if active_buffer:
                line = cursor.line
                column = cursor.column
                text_buffer.delete_in_line(
                    line_number=cursor.line, column_number=column
                )
                if column >= len(text_buffer.get_line(line)):
                    cursor.move_left()
                return TransitionType.STAY
            case ("X",) if active_buffer:
                line = cursor.line
                column = cursor.column
                if column > 0:
                    text_buffer.delete_in_line(
                        line_number=line, column_number=column - 1
                    )
                    cursor.move_left()
                return TransitionType.STAY
            case ("d", "d") if active_buffer:
                line = cursor.line
                text_buffer.delete_line(line)
                if line >= text_buffer.number_of_lines():
                    cursor.move_up()
                cursor.column = 0
                return TransitionType.STAY
            case ("i",) if active_buffer:
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("a",) if active_buffer:
                cursor.allow_extra_column = True
                cursor.move_right()
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("I",) if active_buffer:
                cursor.column = 0
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("A",) if active_buffer:
                cursor.allow_extra_column = True
                cursor.column = -1
                cursor.move_right()
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("o",) if active_buffer:
                line_number = cursor.line + 1
                text_buffer.insert_line(line_number)
                cursor.set(line=line_number, column=0)
                return (TransitionType.SWITCH, "INSERT MODE")
            case ("O",) if active_buffer:
                line_number = cursor.line
                text_buffer.insert_line(line_number)
                cursor.set(line=line_number, column=0)
                return (TransitionType.SWITCH, "INSERT MODE")
            case (":",):
                return (TransitionType.SWITCH, "COMMAND MODE")
            case ("Z", "Z"):
                if active_buffer:
                    self._text_buffer_manager.save_buffer()
                return TransitionType.QUIT
            case ("Z", "Q"):
                return TransitionType.QUIT
            case cmd if cmd in _COMMANDS:
                return TransitionType.STAY
            case _:
                raise ValueError(f"Unknown command: {command}.")
