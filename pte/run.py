#!/usr/bin/env python3

import argparse
import curses
import logging
import os
from pathlib import Path
from importlib import metadata

from pte import modes
from pte.document_buffer_manager import DocumentBufferManager
from pte.view import MainView


log = logging.getLogger("pte.run")


def set_up_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    log_directory = Path(os.environ["XDG_DATA_HOME"]) / "pte" / "log"
    log_directory.mkdir(parents=True, exist_ok=True)

    fh = logging.FileHandler(log_directory / "log.txt", "w+")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pte", description="A modal command-line text editor written in Python"
    )
    parser.add_argument("filename", nargs="?")
    parser.add_argument("-v", "--version", action="version", version=metadata.version("pte"))
    return parser.parse_args()


def run(stdscr: curses.window, args: argparse.Namespace) -> None:
    log.info("Starting up...")

    log.info("Setting up view.")

    curses.set_escdelay(1)
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    view = MainView(stdscr)

    log.info("Setting up document buffer manager.")

    document_buffer_manager = DocumentBufferManager()

    log.info("Setting up modes.")

    normal = modes.NormalMode(document_buffer_manager, view)
    insert = modes.InsertMode(document_buffer_manager, view)
    command = modes.CommandMode(document_buffer_manager, view)

    log.info("Initializing buffers.")

    if args.filename:
        document_buffer_manager.load_file(Path(args.filename))

    log.info("Run mode machine.")

    mode_machine = modes.ModeMachine(normal, insert, command)
    mode_machine.switch_mode(normal)
    mode_machine.run()

    log.info("Exit.")


def main() -> None:
    args = get_args()
    set_up_logging()
    curses.wrapper(run, args)


if __name__ == "__main__":
    main()
