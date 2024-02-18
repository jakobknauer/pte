import logging

from .cursor import Cursor
from .document import Document
from .syntax_highlighting import NoOpHighlighter, SyntaxHighlighter


log = logging.getLogger(__name__)


class DocumentBuffer:
    def __init__(
        self,
        document: Document,
        cursor: Cursor | None = None,
        highlighter: SyntaxHighlighter | None = None,
    ) -> None:
        self.document: Document = document
        self.cursor: Cursor = cursor or Cursor(document)

        self._highlighter: SyntaxHighlighter = NoOpHighlighter()
        if highlighter:
            self.highlighter = highlighter

    @property
    def highlighter(self) -> SyntaxHighlighter:
        return self._highlighter

    @highlighter.setter
    def highlighter(self, highlighter: SyntaxHighlighter) -> None:
        self.document.unsubscribe(self._highlighter.update)
        self._highlighter = highlighter
        self.document.subscribe(highlighter.update)
        log.info(f"Setting highlighter: '{highlighter}'.")
