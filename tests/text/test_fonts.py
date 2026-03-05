from __future__ import annotations

import io
from pathlib import Path

import pytest

from pptx.text.fonts import (
    FontFiles,
    _BaseTable,
    _Font,
    _HeadTable,
    _NameTable,
    _Stream,
    _TableFactory,
)


def test_font_open_context_manager(test_files_dir: Path) -> None:
    font_path = test_files_dir / "calibriz.ttf"

    with _Font.open(str(font_path)) as font:
        assert isinstance(font, _Font)


def test_font_properties_from_real_file(test_files_dir: Path) -> None:
    font_path = test_files_dir / "calibriz.ttf"

    with _Font.open(str(font_path)) as font:
        assert font.family_name == "Calibri"
        assert font.is_bold is True
        assert font.is_italic is True


def test_font_files_find_uses_cache(monkeypatch: pytest.MonkeyPatch, test_files_dir: Path) -> None:
    expected_path = str(test_files_dir / "calibriz.ttf")

    FontFiles._font_files = None
    monkeypatch.setattr(
        FontFiles,
        "_installed_fonts",
        lambda: {("Calibri", True, True): expected_path},
    )

    assert FontFiles.find("Calibri", True, True) == expected_path
    assert FontFiles.find("Calibri", True, True) == expected_path


@pytest.mark.parametrize(
    ("platform", "expected_prefix"),
    [
        ("darwin", "/Library/Fonts"),
        ("win32", r"C:\Windows\Fonts"),
    ],
)
def test_font_files_directories_by_platform(
    monkeypatch: pytest.MonkeyPatch, platform: str, expected_prefix: str
) -> None:
    monkeypatch.setattr("sys.platform", platform)

    directories = FontFiles._font_directories()

    assert directories[0] == expected_prefix


def test_font_files_unsupported_os(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.platform", "linux")

    with pytest.raises(OSError, match="unsupported operating system"):
        FontFiles._font_directories()


def test_font_files_os_x_directories_include_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("os.environ", {"HOME": "/Users/tester"})

    directories = FontFiles._os_x_font_directories()

    assert "/Users/tester/Library/Fonts" in directories
    assert "/Users/tester/.fonts" in directories


def test_font_files_iter_font_files_in_filters_extensions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "a.ttf").write_bytes(b"ttf")
    (tmp_path / "b.otf").write_bytes(b"otf")
    (tmp_path / "c.txt").write_bytes(b"txt")

    class _StubFont:
        family_name = "Family"
        is_bold = True
        is_italic = False

        def __enter__(self) -> _StubFont:
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

    monkeypatch.setattr("pptx.text.fonts._Font.open", lambda path: _StubFont())

    paths = list(FontFiles._iter_font_files_in(str(tmp_path)))

    returned_files = {Path(path).name for _, path in paths}
    assert returned_files == {"a.ttf", "b.otf"}


def test_stream_read_and_read_fields() -> None:
    stream = _Stream(io.BytesIO(b"foob\x00\x2a\x00\x15xxxx"))

    assert stream.read(0, 4) == b"foob"
    assert stream.read_fields(">4sHH", 0) == (b"foob", 42, 21)


def test_name_table_decode_name() -> None:
    assert _NameTable._decode_name(b"Arial", 1, 0) == "Arial"
    assert _NameTable._decode_name("Arial".encode("utf-16-be"), 3, 1) == "Arial"
    assert _NameTable._decode_name(b"bad", 2, 0) is None


def test_name_table_raw_name_string() -> None:
    bufr = b"\x00\x00\x00\x00foobar"

    assert _NameTable._raw_name_string(bufr, 4, 0, 6) == b"foobar"


def test_name_table_header() -> None:
    header = _NameTable._name_header(
        b"\x00\x00\x00\x00\x00\x00\x00\x03\x00\x01\x00\x00\x00\x01\x00\x04\x00\x02",
        0,
    )

    assert header == (3, 1, 0, 1, 4, 2)


@pytest.mark.parametrize(
    ("tag", "expected_type"),
    [
        ("head", _HeadTable),
        ("name", _NameTable),
        ("cmap", _BaseTable),
    ],
)
def test_table_factory_dispatch(tag: str, expected_type: type[object]) -> None:
    table_obj = _TableFactory(tag, _Stream(io.BytesIO(b"")), 0, 0)

    assert isinstance(table_obj, expected_type)


def test_head_table_mac_style_bold_italic() -> None:
    head = _HeadTable("head", _Stream(io.BytesIO(b"")), 0, 0)

    head.__dict__["_fields"] = (
        b"\x00\x01\x00\x00",
        b"\x00\x01\x00\x00",
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        3,
        0,
        0,
        0,
        0,
    )

    assert head.is_bold is True
    assert head.is_italic is True


def test_name_table_family_name_priority() -> None:
    name_table = _NameTable("name", _Stream(io.BytesIO(b"")), 0, 0)
    name_table.__dict__["_names"] = {
        (3, 1): "WinName",
        (1, 1): "MacName",
    }

    assert name_table.family_name == "MacName"
