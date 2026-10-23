"""Portable document contract, independent of UI and download engines."""

import math
from dataclasses import asdict, dataclass, field


@dataclass
class Segment:
    start: float
    end: float
    text: str

    def __post_init__(self):
        if (
            not math.isfinite(self.start)
            or not math.isfinite(self.end)
            or self.start < 0
            or self.end < self.start
        ):
            raise ValueError("Invalid segment timestamp")


@dataclass
class Document:
    title: str
    source: str
    language: str
    method: str
    segments: list[Segment]
    chapters: list[dict] = field(default_factory=list)
    notes: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def duration(self):
        return max((s.end for s in self.segments), default=0)

    def to_dict(self):
        return {**asdict(self), "duration": self.duration}
