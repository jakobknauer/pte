import logging

from pte.state import State


class StateMachine:
    def __init__(self, *, logger: logging.Logger | None = None) -> None:
        self._state: State | None = None
        self._logger = logger or logging.getLogger()

    def set_state(self, state: State) -> None:
        self._state = state

    def run(self) -> None:
        self.info(f"Initial state: {self._state}.")

        while self._state:
            self.info(f"Draw {self._state}.")
            try:
                self._state.draw()
            except:
                self.error(f"An error occured in {self._state}.draw().", exc_info=True)
                raise

            self.info(f"Update {self._state}.")
            try:
                next_state = self._state.update()
            except:
                self.error(
                    f"An error occured in {self._state}.update().", exc_info=True
                )
                raise

            self.info(f"Transition from {self._state} to {next_state}.")
            self._state = next_state

    def info(self, *args, **kwargs) -> None:
        self._logger.info(*args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        self._logger.error(*args, **kwargs)
