from dataclasses import dataclass

from pte import colors


@dataclass
class Highlight:
    column: int
    length: int
    foreground: colors.Color
