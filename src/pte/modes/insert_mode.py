import string

from pte import colors
from pte.document_buffer import DocumentBuffer
from pte.document_buffer_manager import DocumentBufferManager
from pte.view import MainView

from .mode import Mode
from .transition import Transition, TransitionType


ESCAPE = "\x1b"
DEL = "KEY_DC"
BACKSPACE = "KEY_BACKSPACE"
RETURN = "\n"
TAB = "\t"

SPACES_PER_TAB = 4


class InsertMode(Mode):
    def __init__(self, document_buffer_manager: DocumentBufferManager, view: MainView):
        super().__init__(name="INSERT MODE")
        self._document_buffer_manager = document_buffer_manager
        self._view = view
        self._command_buffer: list[str] = []

        self._document_buffer: DocumentBuffer | None = None

    def enter(self, **_: object) -> None:
        if not self._document_buffer_manager.active_buffer:
            raise NotImplementedError("Cannot run insert mode without active buffer.")

        self._document_buffer = self._document_buffer_manager.active_buffer
        self._document_buffer.cursor.allow_extra_column = True
        self._document_buffer.highlighter.update()

        self._view.document = list(self._document_buffer.document)
        self._view.status = self.name
        self._view.status_color = colors.GREEN

    def leave(self) -> None:
        self._view.status = f"LEFT {self.name}"
        self._command_buffer.clear()

    def draw(self) -> None:
        if not self._document_buffer:
            raise NotImplementedError("Cannot run insert mode without active buffer.")

        self._view.document = list(self._document_buffer.document)
        self._view.cursor = (self._document_buffer.cursor.line, self._document_buffer.cursor.column)

        self._view.highlights = [
            self._document_buffer.highlighter.get_highlights(line)
            for line in range(self._document_buffer.document.number_of_lines())
        ]

        self._view.draw()

    def update(self) -> Transition:
        if not self._document_buffer:
            raise NotImplementedError("Cannot run insert mode without active buffer.")

        self._command_buffer.append(self._view.read())

        document = self._document_buffer.document
        cursor = self._document_buffer.cursor

        match self._command_buffer:
            case [c] if c == ESCAPE:
                self._command_buffer.clear()
                cursor.move_left()
                return (TransitionType.SWITCH, "NORMAL MODE")

            case [c] if c == RETURN:
                self._command_buffer.clear()
                document.split_line(line_number=cursor.line, column_number=cursor.column)
                cursor.move_down()
                cursor.column = 0
                return TransitionType.STAY

            case [c] if c == TAB:
                self._command_buffer.clear()
                spaces = SPACES_PER_TAB * " "
                document.insert(line_number=cursor.line, column_number=cursor.column, text=spaces)
                cursor.move_right(SPACES_PER_TAB)
                return TransitionType.STAY

            case [str(c)] if len(c) == 1 and c in string.printable:
                self._command_buffer.clear()
                document.insert(line_number=cursor.line, column_number=cursor.column, text=c)
                cursor.move_right()
                return TransitionType.STAY

            case [c] if c == DEL:
                self._command_buffer.clear()

                if cursor.column < document.get_line_length(cursor.line):
                    document.delete_in_line(line_number=cursor.line, column_number=cursor.column)
                elif cursor.line < document.number_of_lines() - 1:
                    document.join_lines(cursor.line)

                return TransitionType.STAY

            case [c] if c == BACKSPACE and cursor.column > 0:
                self._command_buffer.clear()
                document.delete_in_line(line_number=cursor.line, column_number=cursor.column - 1)
                cursor.move_left()
                return TransitionType.STAY

            case [c] if c == BACKSPACE and cursor.line > 0:
                self._command_buffer.clear()
                first_line_length = document.get_line_length(cursor.line - 1)
                document.join_lines(cursor.line - 1)
                cursor.set(cursor.line - 1, first_line_length)
                return TransitionType.STAY

            case _:
                self._command_buffer.clear()
                return TransitionType.STAY
