from functools import wraps
import logging
from pathlib import Path
from typing import Callable, Concatenate, Iterator, ParamSpec, TypeVar


log = logging.getLogger(__name__)


T = TypeVar("T")
P = ParamSpec("P")


def _modifies_document(
    fn: Callable[Concatenate["Document", P], T]
) -> Callable[Concatenate["Document", P], T]:
    @wraps(fn)
    def wrapped_fn(self: "Document", *args: P.args, **kwargs: P.kwargs) -> T:
        return_value: T = fn(self, *args, **kwargs)
        for handler in self._subscribers:  # pylint: disable=protected-access
            handler()
        return return_value

    return wrapped_fn


class Document:
    def __init__(self, lines: list[str], path: Path | None = None):
        self._lines = lines
        self.path = path
        self._subscribers: list[Callable[[], None]] = []

    def number_of_lines(self) -> int:
        return len(self._lines)

    @property
    def is_empty(self) -> bool:
        return not self._lines

    def get_line(self, line_number: int) -> str:
        return self._lines[line_number]

    def get_line_length(self, line_number: int) -> int:
        return len(self.get_line(line_number))

    def __iter__(self) -> Iterator[str]:
        return iter(self._lines)

    @_modifies_document
    def insert(self, line_number: int, column_number: int, text: str) -> None:
        line = self._lines[line_number]
        line = line[:column_number] + text + line[column_number:]
        self._lines[line_number] = line

    @_modifies_document
    def delete_in_line(self, line_number: int, column_number: int, count: int = 1) -> None:
        if column_number < 0:
            return
        line = self._lines[line_number]
        line = line[:column_number] + line[column_number + count :]
        self._lines[line_number] = line

    @_modifies_document
    def split_line(self, line_number: int, column_number: int) -> None:
        line = self._lines[line_number]
        new_line = line[column_number:]
        line = line[:column_number]
        self._lines[line_number] = line
        self._lines.insert(line_number + 1, new_line)

    @_modifies_document
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

    @_modifies_document
    def insert_line(self, line_number: int, text: str = "") -> None:
        self._lines.insert(line_number, text)
        log.debug(f"Inserting line {line_number}.")

    @_modifies_document
    def delete_line(self, line_number: int) -> None:
        if line_number < 0 or line_number >= len(self._lines):
            log.warning(f"Cannot delete line {line_number}.")
            return
        del self._lines[line_number]

    @property
    def text(self) -> str:
        return "\n".join(self._lines)

    def get_coordinates(self, index: int) -> tuple[int, int]:
        line_number = 0
        char_counter = 0

        while char_counter + len(self._lines[line_number]) + 1 <= index:
            char_counter += len(self._lines[line_number]) + 1
            line_number += 1

        return line_number, index - char_counter

    def get_index(self, line: int, column: int) -> int:
        return sum(len(l) + 1 for l in self._lines[:line]) + column

    def subscribe(self, handler: Callable[[], None]) -> None:
        self._subscribers.append(handler)
