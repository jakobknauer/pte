from abc import ABC, abstractmethod
import logging


from .transition import Transition


class Mode(ABC):
    def __init__(self, *, name: str = "", logger: logging.Logger | None = None):
        self.name = name
        self._logger = logger or logging.getLogger()

    @abstractmethod
    def enter(self) -> None:
        ...

    @abstractmethod
    def leave(self) -> None:
        ...

    @abstractmethod
    def draw(self) -> None:
        ...

    @abstractmethod
    def update(self) -> Transition:
        ...

    def __repr__(self) -> str:
        return f"[{self.name}]"
