from __future__ import annotations

import pytest

from pptx.dml.color import ColorFormat, RGBColor
from pptx.enum.dml import MSO_COLOR_TYPE, MSO_THEME_COLOR
from pptx.oxml import parse_xml


def _solid_fill(color_choice_xml: bytes = b""):
    return parse_xml(
        b'<a:solidFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        + color_choice_xml
        + b"</a:solidFill>"
    )


@pytest.mark.parametrize(
    ("color_choice_xml", "expected"),
    [
        (b"", None),
        (b"<a:hslClr/>", MSO_COLOR_TYPE.HSL),
        (b"<a:prstClr/>", MSO_COLOR_TYPE.PRESET),
        (b'<a:schemeClr val="accent1"/>', MSO_COLOR_TYPE.SCHEME),
        (b"<a:scrgbClr/>", MSO_COLOR_TYPE.SCRGB),
        (b'<a:srgbClr val="123456"/>', MSO_COLOR_TYPE.RGB),
        (b"<a:sysClr/>", MSO_COLOR_TYPE.SYSTEM),
    ],
)
def test_color_format_type(color_choice_xml: bytes, expected: MSO_COLOR_TYPE | None) -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(color_choice_xml))

    # Act / Assert
    assert color_format.type == expected


def test_color_format_rgb_setter_rejects_non_rgbcolor() -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(b'<a:srgbClr val="123456"/>'))

    # Act / Assert
    with pytest.raises(ValueError, match="assigned value must be type RGBColor"):
        color_format.rgb = (0x12, 0x34, 0x56)  # type: ignore[assignment]


def test_color_format_rgb_setter_changes_non_rgb_color_to_rgb() -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(b'<a:schemeClr val="accent1"/>'))

    # Act
    color_format.rgb = RGBColor(0x12, 0x34, 0x56)

    # Assert
    assert color_format.type == MSO_COLOR_TYPE.RGB
    assert color_format.rgb == RGBColor(0x12, 0x34, 0x56)


def test_color_format_theme_color_setter_changes_to_scheme_color() -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(b'<a:srgbClr val="123456"/>'))

    # Act
    color_format.theme_color = MSO_THEME_COLOR.ACCENT_6

    # Assert
    assert color_format.type == MSO_COLOR_TYPE.SCHEME
    assert color_format.theme_color == MSO_THEME_COLOR.ACCENT_6


@pytest.mark.parametrize(
    ("color_choice_xml", "expected"),
    [
        (b'<a:srgbClr val="123456"><a:lumOff val="25000"/></a:srgbClr>', 0.25),
        (b'<a:srgbClr val="123456"><a:lumMod val="70000"/></a:srgbClr>', -0.3),
        (b'<a:srgbClr val="123456"/>', 0.0),
    ],
)
def test_color_format_brightness_getter(color_choice_xml: bytes, expected: float) -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(color_choice_xml))

    # Act / Assert
    assert color_format.brightness == pytest.approx(expected)


@pytest.mark.parametrize(
    ("value", "expected_lum_mod", "expected_lum_off"),
    [(0.4, 0.6, 0.4), (-0.25, 0.75, None), (0.0, None, None)],
)
def test_color_format_brightness_setter(
    value: float, expected_lum_mod: float | None, expected_lum_off: float | None
) -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(b'<a:srgbClr val="123456"/>'))

    # Act
    color_format.brightness = value

    # Assert
    srgb_clr = color_format._xFill.eg_colorChoice
    lum_mod = srgb_clr.lumMod.val if srgb_clr.lumMod is not None else None
    lum_off = srgb_clr.lumOff.val if srgb_clr.lumOff is not None else None
    assert lum_mod == expected_lum_mod
    assert lum_off == expected_lum_off


def test_color_format_brightness_setter_validates_range() -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(b'<a:srgbClr val="123456"/>'))

    # Act / Assert
    with pytest.raises(ValueError, match="brightness must be number in range -1.0 to 1.0"):
        color_format.brightness = 1.1

    with pytest.raises(ValueError, match="brightness must be number in range -1.0 to 1.0"):
        color_format.brightness = -1.1


def test_color_format_brightness_setter_raises_when_color_type_is_none() -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill())

    # Act / Assert
    with pytest.raises(ValueError, match="can't set brightness when color.type is None"):
        color_format.brightness = 0.5


@pytest.mark.parametrize(
    "color_choice_xml",
    [
        b"<a:hslClr/>",
        b"<a:prstClr/>",
        b"<a:schemeClr val='accent1'/>",
        b"<a:scrgbClr/>",
        b"<a:sysClr/>",
    ],
)
def test_color_format_rgb_getter_raises_on_non_rgb_color(color_choice_xml: bytes) -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(color_choice_xml))

    # Act / Assert
    with pytest.raises(AttributeError, match="no .rgb property on color type"):
        _ = color_format.rgb


def test_none_color_theme_color_getter_raises() -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill())

    # Act / Assert
    with pytest.raises(AttributeError, match="no .theme_color property on color type"):
        _ = color_format.theme_color


@pytest.mark.parametrize(
    "color_choice_xml",
    [b"<a:srgbClr val='123456'/>", b"<a:hslClr/>", b"<a:sysClr/>"],
)
def test_theme_color_returns_not_theme_color_for_non_scheme_colors(color_choice_xml: bytes) -> None:
    # Arrange
    color_format = ColorFormat.from_colorchoice_parent(_solid_fill(color_choice_xml))

    # Act / Assert
    assert color_format.theme_color == MSO_THEME_COLOR.NOT_THEME_COLOR


def test_rgb_color_value_object_behaviors() -> None:
    # Arrange / Act
    color = RGBColor(0x12, 0x34, 0x56)

    # Assert
    assert str(color) == "123456"
    assert RGBColor.from_string("123456") == color


@pytest.mark.parametrize(
    ("r", "g", "b"),
    [("12", "34", "56"), (-1, 34, 56), (12, 256, 56)],
)
def test_rgb_color_rejects_invalid_values(r, g, b) -> None:
    # Arrange / Act / Assert
    with pytest.raises(ValueError, match="RGBColor\\(\\) takes three integer values 0-255"):
        RGBColor(r, g, b)
