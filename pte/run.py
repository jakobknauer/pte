#!/usr/bin/env python3

import curses

from pte import modes
from pte.text_buffer import TextBuffer
from pte.view import MainView
from pte.command_buffer import CommandBuffer


def main(stdscr: curses.window):
    curses.set_escdelay(1)
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    view = MainView(stdscr)
    command_buffer = CommandBuffer(stdscr)

    with open("example.txt") as fp:
        text_buffer = TextBuffer.from_file(fp)

    normal = modes.NormalMode(text_buffer, view, command_buffer)
    insert = modes.InsertMode(text_buffer, view, command_buffer)
    command = modes.CommandMode(text_buffer, view, command_buffer)

    mode_machine = modes.ModeMachine(normal, insert, command)
    mode_machine.switch_mode(normal)
    mode_machine.run()


if __name__ == "__main__":
    curses.wrapper(main)
