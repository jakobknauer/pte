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

    @property
    def max_line(self) -> int:
        if self._document.is_empty:
            return 0
        else:
            return self._document.number_of_lines() - 1

    @property
    def max_column(self) -> int:
        if self._document.is_empty:
            return 0
        elif self.allow_extra_column:
            return self._document.get_line_length(self._line)
        else:
            return self._document.get_line_length(self._line) - 1

    def set(self, line: int, column: int) -> None:
        self._line = max(0, min(line, self.max_line))
        self._column = max(0, min(column, self.max_column))

    def move_up(self, lines: int = 1) -> None:
        self.set(self.line - lines, self.column)

    def move_down(self, lines: int = 1) -> None:
        self.set(self.line + lines, self.column)

    def move_left(self, columns: int = 1) -> None:
        self.set(self.line, max(0, self.column - columns))

    def move_right(self, columns: int = 1) -> None:
        self.set(self.line, self.column + columns)
