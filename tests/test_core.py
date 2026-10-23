import json

import pytest

from mdeverything.export import markdown, srt, write_document
from mdeverything.models import Document, Segment
from mdeverything.pipeline import choose_caption, convert, validate_url
from mdeverything.subtitles import parse_subtitles

VTT = """WEBVTT

00:00.000 --> 00:02.000
Hello world.

00:01.500 --> 00:04.000
Hello world.
This is a test.

00:05.000 --> 00:06.000
Hello world.
"""


def test_rolling_captions_keep_new_text_and_later_repetition():
    segments = parse_subtitles(VTT)
    assert [s.text for s in segments] == ["Hello world.", "This is a test.", "Hello world."]
    assert segments[1].start == 1.5


def test_srt_unicode_html_entities_and_multiline():
    segments = parse_subtitles("1\n00:00:01,250 --> 00:00:03,000\n<b>你好</b> &amp; 世界\n第二行\n")
    assert segments == [Segment(1.25, 3.0, "你好 & 世界 第二行")]


def test_vtt_ignores_metadata_blocks():
    text = "WEBVTT\n\nNOTE 00:00.000 --> 00:02.000\nignore\n\nSTYLE\n::cue { color: red }\n\n00:03.000 --> 00:04.000\nReal text\n"
    assert [s.text for s in parse_subtitles(text)] == ["Real text"]


def test_empty_or_invalid_captions_fail():
    with pytest.raises(ValueError):
        parse_subtitles("WEBVTT\n\nNo speech")
    with pytest.raises(ValueError):
        parse_subtitles("00:05.000 --> 00:02.000\ninvalid")


def test_export_preserves_source_and_escapes_markup(tmp_path):
    doc = Document(
        title='A: "lecture"',
        source="https://www.youtube.com/watch?v=abc",
        language="en",
        method="captions",
        segments=[Segment(65.1, 67.9, "<script>alert(1)</script> [x](javascript:evil)")],
    )
    output = markdown(doc)
    assert "t=65" in output and "00:01:05" in output
    assert "<script>" not in output
    assert "\\[x\\]" in output
    assert "00:01:05,100 --> 00:01:07,900" in srt(doc)
    write_document(doc, tmp_path)
    assert json.loads((tmp_path / "document.json").read_text())["title"] == doc.title


def test_local_conversion_needs_no_model(tmp_path):
    source = tmp_path / "lecture.vtt"
    source.write_text(VTT)
    doc = convert(str(source), language="auto", model="base")
    assert doc.title == "lecture" and doc.method == "subtitles"
    assert len(doc.segments) == 3


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://localhost/a",
        "http://127.0.0.1/a",
        "http://169.254.169.254",
        "http://[::1]/a",
        "https://user:pass@example.com/a",
        "javascript:alert(1)",
        "http://10.1.1.1",
        "https://example.com:22",
    ],
)
def test_invalid_url_rejected(url):
    with pytest.raises(ValueError):
        validate_url(url)


def test_url_and_caption_preference():
    assert validate_url(" https://www.youtube.com/watch?v=abc ") == "https://www.youtube.com/watch?v=abc"
    info = {"subtitles": {"fr": [{}], "en": [{}]}, "automatic_captions": {"zh": [{}]}}
    assert choose_caption(info, "zh") == ("zh", "automatic_captions")
    assert choose_caption(info, "en") == ("en", "subtitles")
    assert choose_caption(info, "ja") is None


def test_silence_not_success_and_missing_file():
    with pytest.raises(FileNotFoundError):
        convert("/no/such/video.mp4")


def test_srt_adjacent_repeated_speech_is_preserved():
    text = "1\n00:00:00,000 --> 00:00:01,000\nYes\n\n2\n00:00:01,000 --> 00:00:02,000\nYes\n"
    assert [s.text for s in parse_subtitles(text)] == ["Yes", "Yes"]


@pytest.mark.parametrize("url", ["http://127.1/a", "http://127.000.0.1/a", "http://0x7f.0.0.1/a"])
def test_numeric_localhost_aliases_rejected(url):
    with pytest.raises(ValueError):
        validate_url(url)


def test_cli_title_cannot_escape_output(tmp_path, monkeypatch):
    from mdeverything import cli

    monkeypatch.setattr(
        cli, "convert", lambda *a, **kw: Document("..", "test", "en", "subtitles", [Segment(0, 1, "safe")])
    )
    sentinel = tmp_path / "document.md"
    sentinel.write_text("keep me")
    assert cli.main(["convert", "test.vtt", "-o", str(tmp_path / "new-output")]) == 0
    assert sentinel.read_text() == "keep me"
    assert list((tmp_path / "new-output").glob("*/document.md"))


def test_captions_without_video_formats(tmp_path, monkeypatch):
    from yt_dlp import YoutubeDL

    from mdeverything.pipeline import _remote

    class CaptionsOnly(YoutubeDL):
        def extract_info(self, url, download=True, **kwargs):
            return self.process_ie_result(
                {
                    "id": "fixture",
                    "title": "Captions-only source",
                    "extractor": "fixture",
                    "extractor_key": "Fixture",
                    "webpage_url": url,
                    "formats": [],
                    "subtitles": {
                        "en": [
                            {"ext": "vtt", "data": "WEBVTT\n\n00:00.000 --> 00:02.000\nExisting captions\n"}
                        ]
                    },
                },
                download=download,
            )

    monkeypatch.setattr("yt_dlp.YoutubeDL", CaptionsOnly)
    doc = _remote("https://example.com/video", "en", "base", tmp_path, lambda *a: None, None)
    assert doc.method == "captions"
    assert doc.segments[0].text == "Existing captions"
