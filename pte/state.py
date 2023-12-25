from abc import ABC, abstractmethod
import logging


class State(ABC):
    def __init__(self, *, name: str = "", logger: logging.Logger | None = None):
        self._name = name
        self._logger = logger or logging.getLogger()

    @abstractmethod
    def draw(self) -> None:
        ...

    @abstractmethod
    def update(self) -> "State | None":
        ...

    def __repr__(self) -> str:
        return f"[{self._name}]"
