from pathlib import Path
import logging

from .text_buffer import TextBuffer
from .cursor import Cursor


log = logging.getLogger(__name__)


class TextBufferManager:
    def __init__(self) -> None:
        self.buffers: list[tuple[TextBuffer, Cursor]] = []
        self.active_buffer: tuple[TextBuffer, Cursor] | None = None

    def load_file(self, path: Path) -> bool:
        log.info(f"Loading file '{path}'.")
        try:
            with open(path) as fp:
                lines = fp.read().splitlines()
        except IOError as exc:
            log.error(f"The following error occured reading '{path}': {exc}.")
            return False

        log.info(f"Successfully loaded file '{path}'.")
        new_buffer = TextBuffer(lines, path)
        new_cursor = Cursor(new_buffer)
        self.buffers.append((new_buffer, new_cursor))
        self.active_buffer = (new_buffer, new_cursor)
        return True

    def save_buffer(self, path: Path | None = None) -> bool:
        if self.active_buffer is None:
            return False

        path = path or self.active_buffer[0].path
        if not path:
            log.error(
                "Cannot save buffer, as path was neither provided as argument nor stored in buffer."
            )
            return False

        log.info(f"Saving buffer to '{path}'.")

        try:
            with open(path, "w") as fp:
                for line in self.active_buffer[0]:
                    fp.write(f"{line}\n")
        except IOError as exc:
            log.error(f"The following error occured saving buffer to '{path}': {exc}.")
            return False

        log.info(f"Succesfully saved buffer to '{path}'.")
        self.active_buffer[0].path = path
        return True

    def load_empty_buffer(self) -> None:
        log.info("Creating empty buffer.")
        new_buffer = TextBuffer([""])
        new_cursor = Cursor(new_buffer)
        self.buffers.append((new_buffer, new_cursor))
        self.active_buffer = (new_buffer, new_cursor)
