from abc import ABC, abstractmethod
from typing import Optional
import logging


class State(ABC):
    def __init__(self, *, name: str = "", logger: logging.Logger | None = None):
        self._name = name
        self._logger = logger or logging.getLogger()

    @abstractmethod
    def run(self) -> Optional["State"]:
        ...

    def __repr__(self) -> str:
        return f"[{self._name}]"
