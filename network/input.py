from dataclasses import dataclass


@dataclass(frozen=True)
class FrameInput:
    frame: int
    attack: bool = False