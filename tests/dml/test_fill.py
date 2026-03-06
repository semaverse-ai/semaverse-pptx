from __future__ import annotations

import pytest

from pptx.dml.color import ColorFormat
from pptx.dml.fill import (
    FillFormat,
    _BlipFill,
    _Fill,
    _GradFill,
    _GradientStop,
    _GradientStops,
    _GrpFill,
    _NoFill,
    _NoneFill,
    _PattFill,
    _SolidFill,
)
from pptx.enum.dml import MSO_FILL, MSO_PATTERN
from pptx.oxml import parse_xml
from pptx.oxml.dml.fill import CT_GradientStopList


def _sp_pr(fill_xml: bytes = b""):
    return parse_xml(
        b'<p:spPr xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        + fill_xml
        + b"</p:spPr>"
    )


def _a(tag: str, children: bytes = b""):
    return parse_xml(
        f'<a:{tag} xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'.encode("utf-8")
        + children
        + f"</a:{tag}>".encode("utf-8")
    )


def test_fill_format_type_transitions() -> None:
    fill = FillFormat.from_fill_parent(_sp_pr())

    fill.background()
    background_type = fill.type
    fill.gradient()
    gradient_type = fill.type
    fill.patterned()
    patterned_type = fill.type
    fill.solid()
    solid_type = fill.type

    assert background_type == MSO_FILL.BACKGROUND
    assert gradient_type == MSO_FILL.GRADIENT
    assert patterned_type == MSO_FILL.PATTERNED
    assert solid_type == MSO_FILL.SOLID


def test_fill_format_fore_and_back_color_access() -> None:
    fill = FillFormat.from_fill_parent(_sp_pr())
    fill.patterned()

    fore_color = fill.fore_color
    back_color = fill.back_color

    assert isinstance(fore_color, ColorFormat)
    assert isinstance(back_color, ColorFormat)


def test_fill_format_pattern_getter_and_setter() -> None:
    fill = FillFormat.from_fill_parent(_sp_pr())
    fill.patterned()

    fill.pattern = MSO_PATTERN.WAVE

    assert fill.pattern == MSO_PATTERN.WAVE


def test_fill_format_gradient_access_raises_on_non_gradient_fill() -> None:
    fill = FillFormat.from_fill_parent(_sp_pr(b"<a:noFill/>"))

    # Act / Assert
    with pytest.raises(TypeError):
        _ = fill.gradient_angle
    with pytest.raises(TypeError):
        fill.gradient_angle = 30.0
    with pytest.raises(TypeError):
        _ = fill.gradient_stops


def test_fill_format_gradient_angle_and_stops_on_gradient_fill() -> None:
    fill = FillFormat.from_fill_parent(_sp_pr(b'<a:gradFill><a:lin ang="0"/></a:gradFill>'))

    fill.gradient_angle = 42.0
    angle = fill.gradient_angle
    stops = fill.gradient_stops

    assert angle == pytest.approx(42.0)
    assert isinstance(stops, _GradientStops)


def test_fill_factory_returns_correct_fill_type_class() -> None:
    # Arrange / Act / Assert
    assert isinstance(_Fill(None), _NoneFill)
    assert isinstance(_Fill(_a("blipFill")), _BlipFill)
    assert isinstance(_Fill(_a("gradFill")), _GradFill)
    assert isinstance(_Fill(_a("grpFill")), _GrpFill)
    assert isinstance(_Fill(_a("noFill")), _NoFill)
    assert isinstance(_Fill(_a("pattFill")), _PattFill)
    assert isinstance(_Fill(_a("solidFill")), _SolidFill)
    assert isinstance(_Fill(_a("foo")), _Fill)


def test_fill_base_class_exposes_only_common_interface() -> None:
    fill = _Fill("unknown")

    # Act / Assert
    assert not hasattr(fill, "back_color")
    assert not hasattr(fill, "fore_color")
    assert not hasattr(fill, "pattern")
    with pytest.raises(NotImplementedError):
        _ = fill.type


def test_concrete_fill_classes_report_type() -> None:
    # Arrange / Act / Assert
    assert _BlipFill(_a("blipFill")).type == MSO_FILL.PICTURE
    assert _GradFill(_a("gradFill")).type == MSO_FILL.GRADIENT
    assert _GrpFill(_a("grpFill")).type == MSO_FILL.GROUP
    assert _NoFill(_a("noFill")).type == MSO_FILL.BACKGROUND
    assert _NoneFill(None).type is None
    assert _PattFill(_a("pattFill")).type == MSO_FILL.PATTERNED
    assert _SolidFill(_a("solidFill")).type == MSO_FILL.SOLID


def test_grad_fill_gradient_angle_behaviors() -> None:
    grad_fill = _GradFill(_a("gradFill", b'<a:lin ang="0"/>'))
    non_linear_grad_fill = _GradFill(_a("gradFill", b"<a:path/>"))
    inherited_grad_fill = _GradFill(_a("gradFill"))

    # Act / Assert
    assert grad_fill.gradient_angle == 0.0
    grad_fill.gradient_angle = 90.0
    assert grad_fill.gradient_angle == pytest.approx(90.0)

    with pytest.raises(ValueError, match="not a linear gradient"):
        _ = non_linear_grad_fill.gradient_angle

    assert inherited_grad_fill.gradient_angle is None
    with pytest.raises(ValueError, match="not a linear gradient"):
        inherited_grad_fill.gradient_angle = 10.0


def test_patt_fill_properties() -> None:
    patt_fill = _PattFill(_a("pattFill"))

    patt_fill.pattern = MSO_PATTERN.DIVOT
    fore_color = patt_fill.fore_color
    back_color = patt_fill.back_color

    assert patt_fill.pattern == MSO_PATTERN.DIVOT
    assert isinstance(fore_color, ColorFormat)
    assert isinstance(back_color, ColorFormat)


def test_solid_fill_fore_color() -> None:
    solid_fill = _SolidFill(_a("solidFill"))

    fore_color = solid_fill.fore_color

    assert isinstance(fore_color, ColorFormat)


def test_gradient_stops_collection_and_gradient_stop_accessors() -> None:
    gs_lst = CT_GradientStopList.new_gsLst()
    stops = _GradientStops(gs_lst)

    stop = stops[0]
    color = stop.color
    position = stop.position
    stop.position = 0.2

    assert len(stops) == 2
    assert isinstance(stop, _GradientStop)
    assert isinstance(color, ColorFormat)
    assert isinstance(position, float)
    assert stop.position == pytest.approx(0.2)
