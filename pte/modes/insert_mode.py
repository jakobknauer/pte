import string

from pte.text_buffer import TextBuffer
from pte.cursor import Cursor
from pte.view import MainView, colors

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
DEL = "KEY_DC"
BACKSPACE = "KEY_BACKSPACE"
RETURN = "\n"


class InsertMode(Mode):
    def __init__(self, text_buffer: TextBuffer, cursor: Cursor, view: MainView):
        super().__init__(name="INSERT MODE")
        self._text_buffer = text_buffer
        self._cursor = cursor
        self._view = view
        self._command_buffer: list[str] = []

    def enter(self) -> None:
        self._view.text_buffer_view.status = self.name
        self._view.text_buffer_view.status_color = colors.GREEN
        self._cursor.allow_extra_column = True

    def leave(self) -> None:
        self._view.text_buffer_view.status = f"LEFT {self.name}"
        self._command_buffer.clear()

    def draw(self) -> None:
        self._view.text_buffer_view.set_cursor(self._cursor.line, self._cursor.column)
        self._view.text_buffer_view.consolidate_view_parameters()
        self._view.draw()

    def update(self) -> Transition:
        self._command_buffer.append(self._view.read())

        text_buffer = self._text_buffer
        cursor = self._cursor

        match self._command_buffer:
            case [c] if c == ESCAPE:
                self._command_buffer.clear()
                cursor.move_left()
                return (TransitionType.SWITCH, "NORMAL MODE")
            case [c] if c == RETURN:
                self._command_buffer.clear()
                text_buffer.split_line(
                    line_number=cursor.line,
                    column_number=cursor.column,
                )
                cursor.set(line=cursor.line, column=0)
                return TransitionType.STAY
            case [str(c)] if len(c) == 1 and c in string.printable:
                self._command_buffer.clear()
                text_buffer.insert(
                    line_number=cursor.line,
                    column_number=cursor.column,
                    text=c,
                )
                cursor.move_right()
                return TransitionType.STAY
            case [c] if c == DEL:
                self._command_buffer.clear()

                if cursor.column < len(text_buffer.get_line(cursor.line)):
                    text_buffer.delete_in_line(
                        line_number=cursor.line,
                        column_number=cursor.column,
                    )
                elif cursor.line < text_buffer.number_of_lines() - 1:
                    text_buffer.join_lines(cursor.line)

                return TransitionType.STAY
            case [c] if c == BACKSPACE:
                self._command_buffer.clear()
                if cursor.column > 0:
                    text_buffer.delete_in_line(
                        line_number=cursor.line, column_number=cursor.column - 1
                    )
                    cursor.move_left()
                elif cursor.line > 0:
                    first_line_length = len(text_buffer.get_line(cursor.line - 1))
                    text_buffer.join_lines(cursor.line - 1)
                    cursor.set(cursor.line - 1, first_line_length)
                return TransitionType.STAY
            case _:
                self._command_buffer.clear()
                return TransitionType.STAY
