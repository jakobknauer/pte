from pte.state import State
from pte.text_buffer import TextBuffer
from pte.view import View


class NormalMode(State):
    def __init__(self, text_buffer: TextBuffer, view: View):
        super().__init__(name="NORMAL MODE")
        self._text_buffer = text_buffer
        self._view = view
        self._view.set_text_buffer(self._text_buffer)

    def draw(self) -> None:
        self._view.draw()

    def update(self) -> State:
        command = self._view.input()
        if command == "q":
            return None
        return self
