#!/usr/bin/env python3

from curses import wrapper

from pte.state_machine import StateMachine
from pte.text_buffer import TextBuffer
from pte.view import View
from pte.command_buffer import CommandBuffer
from pte import modes


def main(stdscr):
    view = View(stdscr)
    command_buffer = CommandBuffer(stdscr)

    with open("example.txt") as fp:
        text_buffer = TextBuffer.from_file(fp)

    normal = modes.NormalMode(text_buffer, view, command_buffer)
    insert = modes.InsertMode(text_buffer, view, command_buffer)

    normal.set_insert_mode(insert)

    state_machine = StateMachine()
    state_machine.set_state(normal)
    state_machine.run()


if __name__ == "__main__":
    wrapper(main)
