from abc import ABC, abstractmethod
from typing import Self
import logging


class State(ABC):
    def __init__(self, *, name: str = "", logger: logging.Logger | None):
        self._name = name
        self._logger = logger or logging.getLogger()

    @abstractmethod
    def run(self) -> Self | None:
        ...

    def __repr__(self) -> str:
        return f"[{self._name}]"
