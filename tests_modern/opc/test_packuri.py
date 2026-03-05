from __future__ import annotations

import pytest

from pptx.opc.packuri import PackURI


def test_packuri_from_rel_ref() -> None:
    pack_uri = PackURI.from_rel_ref("/ppt/slides", "../slideLayouts/slideLayout1.xml")

    assert pack_uri == "/ppt/slideLayouts/slideLayout1.xml"


def test_packuri_raises_on_bad_str() -> None:
    with pytest.raises(ValueError):
        PackURI("foobar")


@pytest.mark.parametrize(
    ("uri", "expected_value"),
    [
        ("/", "/"),
        ("/ppt/presentation.xml", "/ppt"),
        ("/ppt/slides/slide1.xml", "/ppt/slides"),
    ],
)
def test_packuri_base_uri(uri: str, expected_value: str) -> None:
    assert PackURI(uri).baseURI == expected_value


@pytest.mark.parametrize(
    ("uri", "expected_value"),
    [
        ("/", ""),
        ("/ppt/presentation.xml", "xml"),
        ("/ppt/media/image.PnG", "PnG"),
    ],
)
def test_packuri_ext(uri: str, expected_value: str) -> None:
    assert PackURI(uri).ext == expected_value


@pytest.mark.parametrize(
    ("uri", "expected_value"),
    [
        ("/", ""),
        ("/ppt/presentation.xml", "presentation.xml"),
        ("/ppt/media/image.png", "image.png"),
    ],
)
def test_packuri_filename(uri: str, expected_value: str) -> None:
    assert PackURI(uri).filename == expected_value


@pytest.mark.parametrize(
    ("uri", "expected_value"),
    [
        ("/", None),
        ("/ppt/presentation.xml", None),
        ("/ppt/,foo,grob!.xml", None),
        ("/ppt/media/image42.png", 42),
    ],
)
def test_packuri_idx(uri: str, expected_value: int | None) -> None:
    assert PackURI(uri).idx == expected_value


@pytest.mark.parametrize(
    ("uri", "base_uri", "expected_value"),
    [
        ("/ppt/presentation.xml", "/", "ppt/presentation.xml"),
        ("/ppt/slideMasters/slideMaster1.xml", "/ppt", "slideMasters/slideMaster1.xml"),
        (
            "/ppt/slideLayouts/slideLayout1.xml",
            "/ppt/slides",
            "../slideLayouts/slideLayout1.xml",
        ),
    ],
)
def test_packuri_relative_ref(uri: str, base_uri: str, expected_value: str) -> None:
    assert PackURI(uri).relative_ref(base_uri) == expected_value


@pytest.mark.parametrize(
    ("uri", "expected_value"),
    [
        ("/", "/_rels/.rels"),
        ("/ppt/presentation.xml", "/ppt/_rels/presentation.xml.rels"),
        ("/ppt/slides/slide42.xml", "/ppt/slides/_rels/slide42.xml.rels"),
    ],
)
def test_packuri_rels_uri(uri: str, expected_value: str) -> None:
    assert PackURI(uri).rels_uri == expected_value
