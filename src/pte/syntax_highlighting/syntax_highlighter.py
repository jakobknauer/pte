from typing_extensions import Protocol

from pte.highlight import Highlight


class SyntaxHighlighter(Protocol):
    def update(self) -> None:
        ...

    def get_highlights(self, line: int) -> list[Highlight]:
        ...


class NoOpHighlighter:
    def update(self) -> None:
        pass

    def get_highlights(self, line: int) -> list[Highlight]:  # pylint: disable=unused-argument
        return []
