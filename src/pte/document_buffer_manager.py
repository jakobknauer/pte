from pathlib import Path
import logging

from .document import Document
from .document_buffer import DocumentBuffer
from .syntax_highlighting import SyntaxHighlighter, PythonHighlighter


log = logging.getLogger(__name__)


class DocumentBufferManager:
    def __init__(self) -> None:
        self.buffers: list[DocumentBuffer] = []
        self.active_buffer: DocumentBuffer | None = None

    def load_file(self, path: Path) -> bool:
        log.info(f"Loading file '{path}'.")
        try:
            with open(path) as fp:
                lines = fp.read().splitlines()
        except IOError as exc:
            log.error(f"The following error occured reading '{path}': {exc}.")
            return False
        else:
            log.info(f"Successfully loaded file '{path}'.")

        new_document = Document(lines, path)

        highlighter: SyntaxHighlighter | None = None
        if path.suffix == ".py":
            highlighter = PythonHighlighter(new_document)

        new_buffer = DocumentBuffer(new_document, highlighter=highlighter)
        self.buffers.append(new_buffer)
        self.active_buffer = new_buffer
        return True

    def save_buffer(self, path: Path | None = None) -> bool:
        if self.active_buffer is None:
            return False

        path = path or self.active_buffer.document.path
        if not path:
            log.error(
                "Cannot save buffer, as path was neither provided as argument nor stored in buffer."
            )
            return False

        log.info(f"Saving buffer to '{path}'.")

        try:
            with open(path, "w") as fp:
                for line in self.active_buffer.document:
                    fp.write(f"{line}\n")
        except IOError as exc:
            log.error(f"The following error occured saving buffer to '{path}': {exc}.")
            return False

        log.info(f"Succesfully saved buffer to '{path}'.")
        self.active_buffer.document.path = path
        return True

    def load_empty_buffer(self) -> None:
        log.info("Creating empty buffer.")
        new_document = Document([])
        new_buffer = DocumentBuffer(new_document)
        self.buffers.append(new_buffer)
        self.active_buffer = new_buffer
