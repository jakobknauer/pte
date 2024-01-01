#!/usr/bin/env python3

import argparse
import curses
import logging
import os
from pathlib import Path

from pte import modes
from pte.text_buffer_manager import TextBufferManager
from pte.view import MainView


log = logging.getLogger(__name__)


def set_up_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    log_directory = Path(os.environ["XDG_DATA_HOME"]) / "pte" / "log"
    log_directory.mkdir(parents=True, exist_ok=True)

    fh = logging.FileHandler(log_directory / "log.txt", "w+")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def get_args():
    parser = argparse.ArgumentParser(
        prog="pte", description="A modal command-line text editor written in Python"
    )
    parser.add_argument("filename", nargs="?")
    return parser.parse_args()


def main(stdscr: curses.window, args):
    log.info("Starting up...")

    log.info("Setting up view...")

    curses.set_escdelay(1)
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    view = MainView(stdscr)

    log.info("Setting up text buffer manager.")

    text_buffer_manager = TextBufferManager()

    log.info("Setting up modes...")

    normal = modes.NormalMode(text_buffer_manager, view)
    insert = modes.InsertMode(text_buffer_manager, view)
    command = modes.CommandMode(text_buffer_manager, view)

    log.info("Initializing buffers...")

    if args.filename:
        text_buffer_manager.load_file(Path(args.filename))

    log.info("Start mode machine.")

    mode_machine = modes.ModeMachine(normal, insert, command)
    mode_machine.switch_mode(normal)
    mode_machine.run()

    log.info("Leaving...")


if __name__ == "__main__":
    set_up_logging()
    args = get_args()
    curses.wrapper(main, args)
