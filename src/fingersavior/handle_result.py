from enum import StrEnum


class HandleResult(StrEnum):
    BREAK = "break"  # end the current flow loop
    CONTINUE = "continue"  # next flow
    MISS = "miss"  # next flow,not save last flow
    EXIT = "exit"  # exit script
    RETURN = "return"  # exit current flow loop
