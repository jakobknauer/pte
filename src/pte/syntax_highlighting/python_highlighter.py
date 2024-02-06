from collections import defaultdict
import logging

from pygments.lexers.python import PythonLexer
from pygments.token import Token, _TokenType

from pte import colors
from pte.document import Document
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


class PythonHighlighter:
    def __init__(self, document: Document) -> None:
        self._document = document
        self._lexer = PythonLexer()
        self._highlights: defaultdict[int, list[Highlight]] = defaultdict(list)
        document.subscribe(self.update)

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
