from typing import TextIO


class TextBuffer:
    def __init__(self, lines: list[str]):
        self._lines = lines

    def number_of_lines(self) -> int:
        return len(self._lines)

    def get_line(self, line_number: int) -> str:
        return self._lines[line_number]

    def __iter__(self):
        return iter(self._lines)

    def insert(self, line_number: int, column_number: int, text: str) -> None:
        line = self._lines[line_number]
        line = line[:column_number] + text + line[column_number:]
        self._lines[line_number] = line

    def delete_in_line(
        self, line_number: int, column_number: int, count: int = 1
    ) -> None:
        if column_number < 0:
            return
        line = self._lines[line_number]
        line = line[:column_number] + line[column_number + count :]
        self._lines[line_number] = line

    @staticmethod
    def from_file(fp: TextIO) -> "TextBuffer":
        lines = fp.read().splitlines()
        return TextBuffer(lines)
