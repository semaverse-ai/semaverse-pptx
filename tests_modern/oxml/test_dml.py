from __future__ import annotations

import pytest
from syrupy.assertion import SnapshotAssertion

from pptx.enum.dml import MSO_THEME_COLOR
from pptx.oxml import parse_xml
from pptx.oxml.dml.color import CT_Percentage, CT_SchemeColor, CT_SRgbColor
from pptx.oxml.ns import qn


@pytest.fixture
def scheme_clr() -> CT_SchemeColor:
    return parse_xml(
        '<a:schemeClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="bg1"/>'
    )


@pytest.fixture
def scheme_clr_with_lum_mod() -> CT_SchemeColor:
    return parse_xml(
        '<a:schemeClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="bg1">'
        '<a:lumMod val="75000"/>'
        "</a:schemeClr>"
    )


@pytest.fixture
def scheme_clr_with_lum_off() -> CT_SchemeColor:
    return parse_xml(
        '<a:schemeClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="bg1">'
        '<a:lumOff val="40000"/>'
        "</a:schemeClr>"
    )


def test_base_color_element_lum_mod_getter(
    scheme_clr: CT_SchemeColor, scheme_clr_with_lum_mod: CT_SchemeColor
) -> None:
    assert scheme_clr.lumMod is None
    assert isinstance(scheme_clr_with_lum_mod.lumMod, CT_Percentage)


def test_base_color_element_lum_off_getter(
    scheme_clr: CT_SchemeColor, scheme_clr_with_lum_off: CT_SchemeColor
) -> None:
    assert scheme_clr.lumOff is None
    assert isinstance(scheme_clr_with_lum_off.lumOff, CT_Percentage)


def test_base_color_element_clear_lum(
    scheme_clr_with_lum_mod: CT_SchemeColor,
    scheme_clr_with_lum_off: CT_SchemeColor,
    snapshot: SnapshotAssertion,
) -> None:
    scheme_clr_with_lum_mod.clear_lum()
    scheme_clr_with_lum_off.clear_lum()

    assert str(scheme_clr_with_lum_mod.xml) == snapshot(name="lum_mod_removed")
    assert str(scheme_clr_with_lum_off.xml) == snapshot(name="lum_off_removed")


def test_base_color_element_add_lum_mod(
    scheme_clr: CT_SchemeColor, snapshot: SnapshotAssertion
) -> None:
    lum_mod = scheme_clr.add_lumMod(0.75)

    assert scheme_clr.find(qn("a:lumMod")) is lum_mod
    assert str(scheme_clr.xml) == snapshot


def test_base_color_element_add_lum_off(
    scheme_clr: CT_SchemeColor, snapshot: SnapshotAssertion
) -> None:
    lum_off = scheme_clr.add_lumOff(0.4)

    assert scheme_clr.find(qn("a:lumOff")) is lum_off
    assert str(scheme_clr.xml) == snapshot


def test_ct_percentage_is_used_for_lum_elements() -> None:
    lum_mod = parse_xml(
        '<a:lumMod xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="33333"/>'
    )
    lum_off = parse_xml(
        '<a:lumOff xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="66666"/>'
    )

    assert isinstance(lum_mod, CT_Percentage)
    assert isinstance(lum_off, CT_Percentage)


def test_ct_percentage_knows_value() -> None:
    percentage = parse_xml(
        '<a:lumMod xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="99999"/>'
    )

    assert percentage.val == 0.99999


def test_ct_scheme_color_behaviors(
    scheme_clr: CT_SchemeColor, snapshot: SnapshotAssertion
) -> None:
    assert isinstance(scheme_clr, CT_SchemeColor)
    assert scheme_clr.val == MSO_THEME_COLOR.BACKGROUND_1

    scheme_clr.val = MSO_THEME_COLOR.ACCENT_1

    assert str(scheme_clr.xml) == snapshot


def test_ct_srgb_color_behaviors(snapshot: SnapshotAssertion) -> None:
    srgb_clr = parse_xml(
        '<a:srgbClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="123456"/>'
    )

    assert isinstance(srgb_clr, CT_SRgbColor)
    assert srgb_clr.val == "123456"

    srgb_clr.val = "987654"

    assert str(srgb_clr.xml) == snapshot
