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

    def split_line(self, line_number: int, column_number: int) -> None:
        line = self._lines[line_number]
        new_line = line[column_number:]
        line = line[:column_number]
        self._lines[line_number] = line
        self._lines.insert(line_number + 1, new_line)

    def join_lines(self, first_line_number: int) -> None:
        if first_line_number < 0:
            raise ValueError(
                "Value of first_line_number must be greater than 0 "
                "({first_line_number} provided)."
            )
        if first_line_number >= len(self._lines):
            raise ValueError(
                "Value of first_line_number must be lesser than {len(self._lines)} "
                "({first_line_number} provided)."
            )

        if first_line_number + 1 >= len(self._lines):
            return

        first_line = self._lines[first_line_number]
        second_line = self._lines[first_line_number + 1]

        self._lines[first_line_number] = first_line + second_line
        del self._lines[first_line_number + 1]

    def insert_line(self, line_number: int, text: str = "") -> None:
        self._lines.insert(line_number, text)

    def delete_line(self, line_number: int) -> None:
        del self._lines[line_number]

    @staticmethod
    def from_file(fp: TextIO) -> "TextBuffer":
        lines = fp.read().splitlines()
        return TextBuffer(lines)

    def to_file(self, fp: TextIO) -> None:
        for line in self._lines:
            fp.write(f"{line}\n")
