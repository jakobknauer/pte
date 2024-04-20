from enum import Enum, auto


class TransitionType(Enum):
    STAY = auto()
    SWITCH = auto()
    QUIT = auto()


Transition = TransitionType | tuple[TransitionType, str] | tuple[TransitionType, str, dict[str, object]] | None
