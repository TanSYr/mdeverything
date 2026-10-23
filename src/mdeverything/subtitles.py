"""SRT/WebVTT parsing with conservative rolling-caption deduplication."""

import html
import re

from .models import Segment

TIME = r"(?:\d{2,}:)?\d{2}:\d{2}[.,]\d{3}"
CUE = re.compile(rf"^({TIME})\s+-->\s+({TIME})(?:\s.*)?$")


def seconds(value: str) -> float:
    result = 0.0
    for field in value.replace(",", ".").split(":"):
        result = result * 60 + float(field)
    return result


def parse_subtitles(text: str) -> list[Segment]:
    result = []
    previous_lines: list[str] = []
    previous_end = -1.0
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    is_webvtt = text.startswith("WEBVTT")
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        if not lines or re.match(r"^(NOTE(?:\s|$)|STYLE$|REGION$)", lines[0]):
            continue
        for index, line in enumerate(lines):
            match = CUE.match(line.strip())
            if not match:
                continue
            start, end = (seconds(t) for t in match.groups())
            if end < start:
                continue
            clean_lines = [html.unescape(re.sub(r"<[^>]*>", "", t)).strip() for t in lines[index + 1 :]]
            clean_lines = [" ".join(t.split()) for t in clean_lines if t.strip()]
            fresh = clean_lines
            # Only overlapping WebVTT rolling captions are deduplicated.
            # Independent SRT cues and touching repeated speech are preserved.
            if is_webvtt and start < previous_end:
                for overlap in range(min(len(previous_lines), len(clean_lines)), 0, -1):
                    if previous_lines[-overlap:] == clean_lines[:overlap]:
                        fresh = clean_lines[overlap:]
                        break
            if fresh:
                result.append(Segment(start, end, " ".join(fresh)))
            previous_lines, previous_end = clean_lines, end
            break
    if not result:
        raise ValueError("No readable subtitle cues found. Upload a valid UTF-8 SRT or WebVTT file.")
    return result
