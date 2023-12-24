#!/usr/bin/env python3

from pte.state_machine import StateMachine
from pte.text_buffer import TextBuffer
from pte.view import View
from pte import modes


def main():
    with View() as view:
        with open("example.txt") as fp:
            text_buffer = TextBuffer.from_file(fp)

        normal = modes.NormalMode(text_buffer, view)

        state_machine = StateMachine()
        state_machine.set_state(normal)
        state_machine.run()


if __name__ == "__main__":
    main()
