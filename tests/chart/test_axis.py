from __future__ import annotations

# ruff: noqa: E501
import pytest

from pptx.chart.axis import (
    AxisTitle,
    CategoryAxis,
    DateAxis,
    MajorGridlines,
    TickLabels,
    ValueAxis,
    _BaseAxis,
)
from pptx.dml.chtfmt import ChartFormat
from pptx.enum.chart import XL_AXIS_CROSSES, XL_CATEGORY_TYPE, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.oxml import parse_xml
from tests.stubs import PartProviderStub


def _cat_ax(xml_body: bytes = b"") -> object:
    return parse_xml(
        b"""
        <c:catAx xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
          <c:axId val='1'/>
          <c:scaling><c:orientation val='minMax'/></c:scaling>
          <c:crossAx val='2'/>
        """
        + xml_body
        + b"</c:catAx>"
    )


def _val_ax(xml_body: bytes = b"") -> object:
    return parse_xml(
        b"""
        <c:valAx xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
          <c:axId val='2'/>
          <c:scaling><c:orientation val='minMax'/></c:scaling>
          <c:crossAx val='1'/>
        """
        + xml_body
        + b"</c:valAx>"
    )


def test_base_axis_title_and_format() -> None:
    axis = _BaseAxis(_cat_ax())

    assert axis.has_title is False

    axis.has_title = True

    assert axis.has_title is True
    assert isinstance(axis.axis_title, AxisTitle)
    assert isinstance(axis.format, ChartFormat)


def test_axis_title_exposes_part_from_underlying_element() -> None:
    part = object()
    axis_title = AxisTitle(PartProviderStub(part=part))

    resolved_part = axis_title.part

    assert resolved_part is part


def test_base_axis_gridlines_and_ticks() -> None:
    axis = _BaseAxis(_cat_ax())

    assert axis.has_major_gridlines is False
    assert axis.has_minor_gridlines is False
    assert axis.major_tick_mark == XL_TICK_MARK.CROSS
    assert axis.minor_tick_mark == XL_TICK_MARK.CROSS

    axis.has_major_gridlines = True
    axis.has_minor_gridlines = True
    axis.major_tick_mark = XL_TICK_MARK.OUTSIDE
    axis.minor_tick_mark = XL_TICK_MARK.INSIDE

    assert axis.has_major_gridlines is True
    assert axis.has_minor_gridlines is True
    assert axis.major_tick_mark == XL_TICK_MARK.OUTSIDE
    assert axis.minor_tick_mark == XL_TICK_MARK.INSIDE
    assert isinstance(axis.major_gridlines, MajorGridlines)


def test_base_axis_scale_reverse_visible() -> None:
    axis = _BaseAxis(_cat_ax())

    assert axis.maximum_scale is None
    assert axis.minimum_scale is None
    assert axis.reverse_order is False

    axis.maximum_scale = 12.5
    axis.minimum_scale = 2.5
    axis.reverse_order = True
    axis.visible = True

    assert axis.maximum_scale == 12.5
    assert axis.minimum_scale == 2.5
    assert axis.reverse_order is True
    assert axis.visible is True


def test_base_axis_visible_raises_on_non_bool() -> None:
    axis = _BaseAxis(_cat_ax())

    with pytest.raises(ValueError):
        setattr(axis, "visible", "yes")


def test_base_axis_tick_labels() -> None:
    labels = TickLabels(_cat_ax())

    assert labels.number_format == "General"
    assert labels.number_format_is_linked is False
    assert labels.offset == 100

    labels.number_format = "0.00"
    labels.number_format_is_linked = True
    labels.offset = 250

    assert labels.number_format == "0.00"
    assert labels.number_format_is_linked is True
    assert labels.offset == 250


def test_base_axis_tick_label_position() -> None:
    axis = _BaseAxis(_cat_ax())

    assert axis.tick_label_position == XL_TICK_LABEL_POSITION.NEXT_TO_AXIS

    axis.tick_label_position = XL_TICK_LABEL_POSITION.HIGH

    assert axis.tick_label_position == XL_TICK_LABEL_POSITION.HIGH


def test_category_axis_category_type() -> None:
    axis = CategoryAxis(_cat_ax())

    assert axis.category_type == XL_CATEGORY_TYPE.CATEGORY_SCALE


def test_date_axis_category_type() -> None:
    axis = DateAxis(_cat_ax())

    assert axis.category_type == XL_CATEGORY_TYPE.TIME_SCALE


def test_value_axis_crosses_and_units() -> None:
    plot_area = parse_xml(
        b"""
        <c:plotArea xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
          <c:valAx>
            <c:axId val='2'/>
            <c:scaling><c:orientation val='minMax'/></c:scaling>
            <c:crossAx val='1'/>
          </c:valAx>
          <c:catAx>
            <c:axId val='1'/>
            <c:scaling><c:orientation val='minMax'/></c:scaling>
            <c:crossAx val='2'/>
          </c:catAx>
        </c:plotArea>
        """
    )
    axis = ValueAxis(plot_area.xpath("c:valAx")[0])

    assert axis.crosses == XL_AXIS_CROSSES.CUSTOM
    assert axis.crosses_at is None
    assert axis.major_unit is None
    assert axis.minor_unit is None

    axis.crosses = XL_AXIS_CROSSES.MAXIMUM
    axis.crosses_at = 1.25
    axis.major_unit = 2.0
    axis.minor_unit = 0.5

    assert axis.crosses == XL_AXIS_CROSSES.CUSTOM
    assert axis.crosses_at == 1.25
    assert axis.major_unit == 2.0
    assert axis.minor_unit == 0.5
