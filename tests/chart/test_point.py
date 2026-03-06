from __future__ import annotations

# ruff: noqa: E501
import pytest

from pptx.chart.point import BubblePoints, CategoryPoints, Point, XyPoints
from pptx.oxml import parse_xml


def test_category_points_and_point() -> None:
    ser = parse_xml(
        b'<c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:idx val='0'/><c:order val='0'/>"
        b"<c:cat><c:numRef><c:numCache><c:ptCount val='3'/></c:numCache></c:numRef></c:cat>"
        b"</c:ser>"
    )
    points = CategoryPoints(ser)

    assert len(points) == 3
    assert isinstance(points[1], Point)


def test_xy_points_and_bubble_points() -> None:
    xy_ser = parse_xml(
        b"""
        <c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
          <c:idx val='0'/>
          <c:order val='0'/>
          <c:xVal><c:numRef><c:numCache><c:ptCount val='2'/></c:numCache></c:numRef></c:xVal>
          <c:yVal><c:numRef><c:numCache><c:ptCount val='3'/></c:numCache></c:numRef></c:yVal>
        </c:ser>
        """
    )
    bubble_ser = parse_xml(
        b"""
        <c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
          <c:idx val='0'/>
          <c:order val='0'/>
          <c:xVal><c:numRef><c:numCache><c:ptCount val='4'/></c:numCache></c:numRef></c:xVal>
          <c:yVal><c:numRef><c:numCache><c:ptCount val='3'/></c:numCache></c:numRef></c:yVal>
          <c:bubbleSize><c:numRef><c:numCache><c:ptCount val='2'/></c:numCache></c:numRef></c:bubbleSize>
        </c:ser>
        """
    )

    assert len(XyPoints(xy_ser)) == 2
    assert len(BubblePoints(bubble_ser)) == 2


def test_point_properties() -> None:
    ser = parse_xml(
        b'<c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:idx val='0'/><c:order val='0'/></c:ser>"
    )
    point = Point(ser, 0)

    assert point.data_label is not None
    assert point.format is not None
    assert point.marker is not None


def test_points_index_out_of_range() -> None:
    ser = parse_xml(
        b"""
        <c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
          <c:idx val='0'/>
          <c:order val='0'/>
          <c:cat><c:numRef><c:numCache><c:ptCount val='1'/></c:numCache></c:numRef></c:cat>
        </c:ser>
        """
    )
    points = CategoryPoints(ser)

    with pytest.raises(IndexError):
        _ = points[1]
