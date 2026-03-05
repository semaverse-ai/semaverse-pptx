from __future__ import annotations

import pytest

from pptx.dml.color import ColorFormat
from pptx.dml.fill import FillFormat
from pptx.dml.line import LineFormat
from pptx.enum.dml import MSO_FILL, MSO_LINE
from pptx.oxml import parse_xml
from pptx.util import Emu


def _sp_pr(ln_xml: bytes = b""):
    return parse_xml(
        b'<p:spPr xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">' + ln_xml + b"</p:spPr>"
    )


@pytest.mark.parametrize(
    ("ln_xml", "expected"),
    [
        (b"", None),
        (b"<a:ln/>", None),
        (b'<a:ln><a:prstDash val="dash"/></a:ln>', MSO_LINE.DASH),
    ],
)
def test_line_format_dash_style_getter(ln_xml: bytes, expected: MSO_LINE | None) -> None:
    line = LineFormat(_sp_pr(ln_xml))

    dash_style = line.dash_style

    assert dash_style == expected


@pytest.mark.parametrize(
    ("initial_ln_xml", "dash_style", "expect_prst_dash"),
    [
        (b"", MSO_LINE.ROUND_DOT, True),
        (b"<a:ln/>", MSO_LINE.LONG_DASH, True),
        (b"<a:ln><a:custDash/></a:ln>", MSO_LINE.DASH_DOT, True),
        (b"", None, False),
        (b'<a:ln><a:prstDash val="dash"/></a:ln>', None, False),
    ],
)
def test_line_format_dash_style_setter(
    initial_ln_xml: bytes, dash_style: MSO_LINE | None, expect_prst_dash: bool
) -> None:
    sp_pr = _sp_pr(initial_ln_xml)
    line = LineFormat(sp_pr)

    line.dash_style = dash_style

    ln = sp_pr.ln
    if ln is None:
        assert dash_style is None
        return
    assert (ln.prstDash is not None) is expect_prst_dash
    assert ln.custDash is None


def test_line_format_fill_property_creates_ln() -> None:
    sp_pr = _sp_pr()
    line = LineFormat(sp_pr)

    fill = line.fill

    assert isinstance(fill, FillFormat)
    assert sp_pr.ln is not None


def test_line_format_color_property_makes_fill_solid() -> None:
    sp_pr = _sp_pr(b"<a:ln><a:noFill/></a:ln>")
    line = LineFormat(sp_pr)

    color = line.color

    assert isinstance(color, ColorFormat)
    assert line.fill.type == MSO_FILL.SOLID
    assert sp_pr.ln.solidFill is not None


@pytest.mark.parametrize(
    ("ln_xml", "expected"),
    [
        (b"", Emu(0)),
        (b'<a:ln w="12700"/>', Emu(12700)),
    ],
)
def test_line_format_width_getter(ln_xml: bytes, expected: Emu) -> None:
    line = LineFormat(_sp_pr(ln_xml))

    width = line.width

    assert width == expected


@pytest.mark.parametrize(("value", "expected"), [(None, Emu(0)), (12700, Emu(12700))])
def test_line_format_width_setter(value: int | None, expected: Emu) -> None:
    sp_pr = _sp_pr()
    line = LineFormat(sp_pr)

    line.width = value

    assert sp_pr.ln.w == expected
