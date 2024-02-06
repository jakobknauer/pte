import logging
import re
from typing import Pattern

from pte import colors
from pte.document_buffer import DocumentBuffer
from pte.highlight import Highlight


log = logging.getLogger(__name__)


class RegexHighlighter:
    def __init__(self, document_buffer: DocumentBuffer, pattern: str) -> None:
        self._document_buffer = document_buffer
        self._highlights: list[list[Highlight]] = []

        self._pattern: Pattern[str] | None
        try:
            self._pattern = re.compile(pattern)
        except re.error:
            log.debug(f"Not a valid regular expression: '{pattern}'.")
            self._pattern = None

    def update(self) -> None:
        if not self._pattern:
            self._highlights = [[] for _ in self._document_buffer.document]
            log.debug("Pattern is None. No highlights computed.")
            return

        document = self._document_buffer.document
        cursor = self._document_buffer.cursor

        self._highlights = [
            [
                Highlight(match.start(0), match.end(0) - match.start(0), colors.BLACK_ON_YELLOW)
                for match in self._pattern.finditer(line)
            ]
            for line in document
        ]

        cursor_position = document.get_index(cursor.line, cursor.column)
        next_match = self._pattern.search(document.text, cursor_position + 1)
        if next_match:
            next_match_index = next_match.start()
            line, column = document.get_coordinates(next_match_index)
            self._highlights[line].append(
                Highlight(column, next_match.end() - next_match.start(), colors.BLACK_ON_GREEN)
            )

        log.debug(f"Number of highlights: {sum(map(len, self._highlights))}.")

    def get_highlights(self, line: int) -> list[Highlight]:
        return self._highlights[line]
