import logging

from .mode import Mode
from .transition import TransitionType


class ModeMachine:
    def __init__(self, *modes: Mode, logger: logging.Logger | None = None) -> None:
        self._mode: Mode | None = None
        self._modes = {mode.name: mode for mode in modes}
        self._logger = logger or logging.getLogger(__name__)

    def switch_mode(self, new_mode: Mode | None) -> None:
        old_mode = self._mode

        self.info(f"Transitioning from {old_mode} to {new_mode}.")

        if old_mode:
            old_mode.leave()

        self._mode = new_mode

        if new_mode:
            new_mode.enter()

        self.debug(f"Transitioned from {old_mode} to {new_mode}.")

    def run(self) -> None:
        self.info(f"Initial mode: {self._mode}.")

        while self._mode:
            self.debug(f"Draw {self._mode}.")
            try:
                self._mode.draw()
            except:
                self.error(f"An error occured in {self._mode}.draw().", exc_info=True)
                raise

            self.debug(f"Update {self._mode}.")
            try:
                transition = self._mode.update()
            except:
                self.error(f"An error occured in {self._mode}.update().", exc_info=True)
                raise

            match transition:
                case TransitionType.STAY:
                    self.debug(f"Stay in {self._mode}.")
                    continue
                case (TransitionType.SWITCH, str(name)) if name in self._modes:
                    new_mode = self._modes[name]
                    self.switch_mode(new_mode)
                    continue
                case (TransitionType.SWITCH, str(name)):
                    self.error(f"Transition to unknown mode with name '{name}' requested.")
                    raise NotImplementedError(
                        f"Transition to unknown mode with name '{name}' requested."
                    )
                case TransitionType.QUIT | None:
                    self.debug(f"Quit from final mode {self._mode}")
                    break
                case _:
                    self.error(f"Invalid transition '{transition}' requested.")
                    raise NotImplementedError(f"Invalid transition '{transition}' requested.")

        self.info(f"Final mode: {self._mode}.")

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def error(self, message: str, *, exc_info: bool = False) -> None:
        self._logger.error(message, exc_info=exc_info)
