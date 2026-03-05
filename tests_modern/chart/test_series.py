from __future__ import annotations

# ruff: noqa: E501
from pptx.chart.series import BarSeries, BubbleSeries, LineSeries, SeriesCollection, XySeries
from pptx.oxml import parse_xml


def test_series_collection() -> None:
    coll = SeriesCollection(
        parse_xml(
            b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:ser><c:idx val='0'/><c:order val='0'/></c:ser>"
            b"<c:ser><c:idx val='1'/><c:order val='1'/></c:ser>"
            b"</c:barChart>"
        )
    )

    assert len(coll) == 2
    assert isinstance(coll[0], BarSeries)
    assert coll[1].index == 1


def test_bar_series() -> None:
    series = BarSeries(
        parse_xml(
            b'<c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:idx val='42'/><c:order val='0'/><c:tx><c:strRef><c:strCache><c:pt idx='0'><c:v>Foobar</c:v></c:pt></c:strCache></c:strRef></c:tx>"
            b"</c:ser>"
        )
    )

    assert series.index == 42
    assert series.name == "Foobar"
    assert series.invert_if_negative is True

    series.invert_if_negative = False

    assert series.invert_if_negative is False


def test_line_series_smooth_and_marker() -> None:
    line_series = LineSeries(
        parse_xml(
            b'<c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:idx val='0'/><c:order val='0'/></c:ser>"
        )
    )

    assert line_series.smooth is True

    line_series.smooth = False

    assert line_series.smooth is False
    assert line_series.marker is not None


def test_xy_and_bubble_series_values_and_points() -> None:
    xy = XySeries(
        parse_xml(
            b'<c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:idx val='0'/><c:order val='0'/><c:yVal><c:numRef><c:numCache><c:ptCount val='2'/>"
            b"<c:pt idx='0'><c:v>1.1</c:v></c:pt><c:pt idx='1'><c:v>2.2</c:v></c:pt>"
            b"</c:numCache></c:numRef></c:yVal>"
            b"<c:xVal><c:numRef><c:numCache><c:ptCount val='2'/></c:numCache></c:numRef></c:xVal>"
            b"</c:ser>"
        )
    )
    bubble = BubbleSeries(
        parse_xml(
            b'<c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:idx val='0'/><c:order val='0'/><c:yVal><c:numRef><c:numCache><c:ptCount val='1'/>"
            b"<c:pt idx='0'><c:v>1.1</c:v></c:pt></c:numCache></c:numRef></c:yVal>"
            b"<c:xVal><c:numRef><c:numCache><c:ptCount val='1'/></c:numCache></c:numRef></c:xVal>"
            b"<c:bubbleSize><c:numRef><c:numCache><c:ptCount val='1'/></c:numCache></c:numRef></c:bubbleSize>"
            b"</c:ser>"
        )
    )

    assert xy.values == (1.1, 2.2)
    assert xy.points is not None
    assert bubble.points is not None
