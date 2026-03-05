from __future__ import annotations

import pytest

from pptx.oxml import parse_xml
from pptx.oxml.shapes.picture import CT_Picture


def test_picture_new_pic() -> None:
    pic = CT_Picture.new_pic(9, "Picture 8", "kittens.jpg", "rId42", 1, 2, 3, 4)

    assert pic.nvPicPr.cNvPr.id == 9
    assert pic.nvPicPr.cNvPr.name == "Picture 8"
    assert pic.blipFill.blip.rEmbed == "rId42"


@pytest.mark.parametrize(
    ("desc", "expected_xml_desc"),
    [
        ("kittens.jpg", "kittens.jpg"),
        ("bits&bobs.png", "bits&amp;bobs.png"),
        ("img&.png", "img&amp;.png"),
        ("im<ag>e.png", "im&lt;ag&gt;e.png"),
    ],
)
def test_picture_new_pic_escapes_desc(desc: str, expected_xml_desc: str) -> None:
    pic = CT_Picture.new_pic(9, "Picture 8", desc, "rId42", 1, 2, 3, 4)

    assert expected_xml_desc in str(pic.xml)


def test_picture_new_ph_pic() -> None:
    pic = CT_Picture.new_ph_pic(9, "Picture 8", "kittens.jpg", "rId42")

    assert pic.nvPicPr.cNvPr.id == 9
    assert pic.blipFill.blip.rEmbed == "rId42"


def test_picture_new_video_pic() -> None:
    pic = CT_Picture.new_video_pic(42, "Media 41", "rId1", "rId2", "rId3", 1, 2, 3, 4)

    assert pic.nvPicPr.cNvPr.id == 42
    assert pic.nvPicPr.cNvPr.name == "Media 41"
    assert pic.blipFill.blip.rEmbed == "rId3"


def test_picture_src_rect_getters() -> None:
    pic = parse_xml(
        '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<p:blipFill><a:srcRect l="10000" t="20000" r="30000" b="40000"/></p:blipFill></p:pic>'
    )

    assert pic.srcRect_l == 0.1
    assert pic.srcRect_t == 0.2
    assert pic.srcRect_r == 0.3
    assert pic.srcRect_b == 0.4


def test_picture_src_rect_getters_defaults() -> None:
    pic = parse_xml(
        '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:blipFill/></p:pic>'
    )

    assert pic.srcRect_l == 0.0
    assert pic.srcRect_t == 0.0
    assert pic.srcRect_r == 0.0
    assert pic.srcRect_b == 0.0


@pytest.mark.parametrize(
    ("side", "value", "expected_attr"),
    [
        ("l", 0.5, 'l="50000"'),
        ("t", 0.2, 't="20000"'),
        ("r", 0.1, 'r="10000"'),
        ("b", 0.9, 'b="90000"'),
    ],
)
def test_picture_src_rect_setters(side: str, value: float, expected_attr: str) -> None:
    pic = parse_xml(
        '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:blipFill/></p:pic>'
    )

    if side == "l":
        pic.srcRect_l = value
    elif side == "t":
        pic.srcRect_t = value
    elif side == "r":
        pic.srcRect_r = value
    else:
        pic.srcRect_b = value

    assert expected_attr in str(pic.xml)


def test_picture_crop_to_fit() -> None:
    pic = parse_xml(
        '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:blipFill/></p:pic>'
    )

    pic.crop_to_fit((1600, 1200), (800, 400))

    assert pic.blipFill.srcRect is not None
    assert pic.srcRect_t > 0
    assert pic.srcRect_b > 0


def test_picture_get_or_add_ln() -> None:
    pic = parse_xml(
        '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:spPr/></p:pic>'
    )

    assert pic.ln is None

    ln = pic.get_or_add_ln()

    assert pic.ln is ln
    assert pic.ln is not None


def test_picture_blip_rid() -> None:
    pic = parse_xml(
        '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<p:blipFill><a:blip r:embed="rId42"/></p:blipFill></p:pic>'
    )

    assert pic.blip_rId == "rId42"


def test_picture_blip_rid_none() -> None:
    pic = parse_xml(
        '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<p:blipFill><a:blip/></p:blipFill></p:pic>"
    )

    assert pic.blip_rId is None
