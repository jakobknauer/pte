from .cursor import Cursor
from .document import Document


class DocumentBuffer:
    def __init__(self, document: Document, cursor: Cursor | None = None) -> None:
        self.document: Document = document
        self.cursor: Cursor = cursor or Cursor(document)
