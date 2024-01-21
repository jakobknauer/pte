from .document import Document


class Cursor:
    def __init__(self, document: Document) -> None:
        self._document = document
        self._line = 0
        self._column = 0
        self.allow_extra_column = False

    @property
    def line(self) -> int:
        return self._line

    @line.setter
    def line(self, line: int) -> None:
        self.set(line, self._column)

    @property
    def column(self) -> int:
        return self._column

    @column.setter
    def column(self, column: int) -> None:
        self.set(self._line, column)

    def set(self, line: int, column: int) -> None:
        self._line = max(0, min(self._document.number_of_lines() - 1, line))

        max_column = (self._document.get_line_length(self._line) - 1) + (
            1 if self.allow_extra_column else 0
        )
        self._column = max(0, min(column, max_column))

    def move_up(self, lines=1) -> None:
        self.set(self.line - lines, self.column)

    def move_down(self, lines=1) -> None:
        self.set(self.line + lines, self.column)

    def move_left(self, columns=1) -> None:
        self.set(self.line, max(0, self.column - columns))

    def move_right(self, columns=1) -> None:
        self.set(self.line, self.column + columns)
