from collections import defaultdict
import logging

import pygments.lexers
from pygments.token import Token, _TokenType

from pte import colors
from pte.documents import Document
from pte.highlight import Highlight


log = logging.getLogger(__name__)


_TOKENTYPE_COLOR_MAP = {
    Token.Comment: colors.GRAY,
    Token.Keyword: colors.BLUE,
    Token.Literal.Number: colors.CYAN,
    Token.Literal.String.Affix: colors.YELLOW,
    Token.Literal.String.Interpol: colors.YELLOW,
    Token.Literal.String: colors.GREEN,
    Token.Name.Builtin: colors.BLUE,
    Token.Name.Class: colors.BRIGHT_YELLOW,
    Token.Name.Function: colors.MAGENTA,
    Token.Operator.Word: colors.BLUE,
}


def _get_color_for_token_type(token_type: _TokenType) -> colors.Color | None:
    for token_family, color in _TOKENTYPE_COLOR_MAP.items():
        if token_type in token_family:
            return color
    return None


class PygmentsHighlighter:
    def __init__(self, document: Document, syntax_name: str | None = None) -> None:
        self._document = document
        self._highlights: defaultdict[int, list[Highlight]] = defaultdict(list)

        self._lexer: pygments.lexer.Lexer
        if syntax_name is not None:
            self._lexer = pygments.lexers.get_lexer_by_name(syntax_name)
            log.info(f"Chose lexer with name '{self._lexer.name}'.")  # type: ignore[attr-defined]
        else:
            self._lexer = pygments.lexers.guess_lexer(document.text)
            log.info(f"Guessed lexer with name '{self._lexer.name}'.")  # type: ignore[attr-defined]

    def update(self) -> None:
        code = self._document.text
        tokens = self._lexer.get_tokens_unprocessed(code)
        self._highlights.clear()

        for index, token_type, value in tokens:
            color = _get_color_for_token_type(token_type)
            if not color:
                continue

            line, column = self._document.get_coordinates(index)

            highlight = Highlight(column, len(value), color)
            self._highlights[line].append(highlight)

        log.debug(f"Number of highlights: {sum(map(len, self._highlights.values()))}.")

    def get_highlights(self, line: int) -> list[Highlight]:
        return self._highlights.get(line, [])

    def __str__(self) -> str:
        return f"{type(self).__name__} with lexer '{self._lexer.name}'"  # type: ignore[attr-defined]
