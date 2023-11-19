from pte.state import State
from pte.text_buffer import TextBuffer


class NormalMode(State):
    def __init__(self, text_buffer: TextBuffer):
        super().__init__(name="NORMAL MODE")
        self._text_buffer = text_buffer

    def run(self) -> State:
        for line in self._text_buffer:
            print(line, end="")
        input()
        return self
