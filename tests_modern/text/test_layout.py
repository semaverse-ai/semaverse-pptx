from __future__ import annotations

import pytest

from pptx.text.layout import TextFitter, _BinarySearchTree, _Line, _LineSource, _rendered_size


def test_binary_search_tree_from_ordered_sequence() -> None:
    bst = _BinarySearchTree.from_ordered_sequence(range(10))

    def in_order(node: object | None) -> list[int]:
        if node is None:
            return []
        return in_order(node._lesser) + [node.value] + in_order(node._greater)

    assert bst.value == 9
    assert bst._lesser.value == 4
    assert bst._greater is None
    assert in_order(bst) == list(range(10))


@pytest.mark.parametrize(
    ("sequence", "predicate", "expected_value"),
    [
        (range(10), lambda value: value < 6.5, 6),
        (range(10), lambda value: value > 9.9, None),
        (range(10), lambda value: value < 0.0, None),
    ],
)
def test_binary_search_tree_find_max(
    sequence: range,
    predicate: object,
    expected_value: int | None,
) -> None:
    bst = _BinarySearchTree.from_ordered_sequence(sequence)

    assert bst.find_max(predicate) == expected_value


def test_line_source_iteration() -> None:
    line_source = _LineSource("foo bar baz")

    pairs = [(line.text, line.remainder) for line in line_source]

    assert pairs == [
        ("foo", _LineSource("bar baz")),
        ("foo bar", _LineSource("baz")),
        ("foo bar baz", _LineSource("")),
    ]


def test_line_source_boolean() -> None:
    assert bool(_LineSource("foo")) is True
    assert bool(_LineSource("")) is False
    assert bool(_LineSource("   ")) is False


def test_line_properties() -> None:
    line = _Line("foobar", _LineSource("rest"))

    assert line.text == "foobar"
    assert str(line.remainder) == "<_LineSource('rest')>"
    assert len(line) == 6


def test_text_fitter_best_fit_font_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "pptx.text.layout._rendered_size",
        lambda text, point_size, font_file: (point_size * len(text), point_size * 2),
    )

    font_size = TextFitter.best_fit_font_size("foo bar", (500, 500), 42, "font.ttf")

    assert isinstance(font_size, int)
    assert 1 <= font_size <= 42


def test_text_fitter_break_line_and_wrap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "pptx.text.layout._rendered_size",
        lambda text, point_size, font_file: (point_size * len(text), point_size),
    )
    fitter = TextFitter(_LineSource("foo bar baz"), (100, 100), "font.ttf")

    line = fitter._break_line(_LineSource("foo bar baz"), 10)
    wrapped = fitter._wrap_lines(_LineSource("foo bar baz"), 10)

    assert isinstance(line, _Line)
    assert wrapped


def test_rendered_size_uses_getbbox(monkeypatch: pytest.MonkeyPatch) -> None:
    class BBoxFont:
        def getbbox(self, text: str) -> tuple[int, int, int, int]:
            return (0, 0, len(text) * 10, 20)

    monkeypatch.setattr("pptx.text.layout._Fonts.font", lambda _path, _size: BBoxFont())

    width, height = _rendered_size("foo", 12, "font.ttf")

    assert width == 381000
    assert height == 254000


def test_rendered_size_fallback_getsize(monkeypatch: pytest.MonkeyPatch) -> None:
    class SizeFont:
        def getsize(self, text: str) -> tuple[int, int]:
            return (len(text) * 9, 18)

    monkeypatch.setattr("pptx.text.layout._Fonts.font", lambda _path, _size: SizeFont())

    width, height = _rendered_size("abcd", 10, "font.ttf")

    assert width == int((36 / 72.0) * 914400)
    assert height == int((18 / 72.0) * 914400)
