#!/usr/bin/env python3

import curses
import logging

from pte import modes
from pte.text_buffer import TextBuffer
from pte.view import MainView


log = logging.getLogger(__name__)


def set_up_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("log/log.txt", "w+")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def main(stdscr: curses.window):
    log.info("Starting up...")

    log.info("Setting up view...")

    curses.set_escdelay(1)
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    view = MainView(stdscr)

    log.info("Reading file...")

    with open("example.txt") as fp:
        text_buffer = TextBuffer.from_file(fp)

    log.info("Setting up modes...")

    normal = modes.NormalMode(text_buffer, view)
    insert = modes.InsertMode(text_buffer, view)
    command = modes.CommandMode(text_buffer, view)

    log.info("Start mode machine.")

    mode_machine = modes.ModeMachine(normal, insert, command)
    mode_machine.switch_mode(normal)
    mode_machine.run()

    log.info("Leaving...")


if __name__ == "__main__":
    set_up_logging()
    curses.wrapper(main)
