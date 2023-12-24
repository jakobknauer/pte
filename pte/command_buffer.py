import curses

class CommandBuffer:
    def __init__(self, stdscr: curses.window):
        self._stdscr = stdscr
        self._store: list[str] = []

    def read(self) -> None:
        self._store.append(self._stdscr.getkey())

    def get_store(self) -> list[str]:
        return self._store

    def clear(self) -> None:
        self._store.clear()
