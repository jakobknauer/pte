from .cursor import Cursor
from .document import Document
from .syntax_highlighting import SyntaxHighlighter, NoOpHighlighter


class DocumentBuffer:
    def __init__(
        self,
        document: Document,
        cursor: Cursor | None = None,
        highlighter: SyntaxHighlighter | None = None,
    ) -> None:
        self.document: Document = document
        self.cursor: Cursor = cursor or Cursor(document)
        self.highlighter: SyntaxHighlighter = highlighter or NoOpHighlighter()
