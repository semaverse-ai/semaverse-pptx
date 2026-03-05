from __future__ import annotations

# ruff: noqa: E501
from collections.abc import Callable

import pytest
from syrupy.assertion import SnapshotAssertion

from pptx.chart.xmlwriter import ChartXmlWriter, SeriesXmlRewriterFactory
from pptx.enum.chart import XL_CHART_TYPE
from tests.chart.factories import (
    chart_space,
    make_bubble_chart_data,
    make_category_chart_data,
    make_xy_chart_data,
)
from tests.xml_utils import serialize_xml


def _category_data() -> object:
    return make_category_chart_data(2, str, 2)


def _xy_data() -> object:
    return make_xy_chart_data(2, 3)


def _bubble_data() -> object:
    return make_bubble_chart_data(2, 3)


CHART_XML_CASES = [
    (XL_CHART_TYPE.AREA, _category_data),
    (XL_CHART_TYPE.AREA_STACKED, _category_data),
    (XL_CHART_TYPE.AREA_STACKED_100, _category_data),
    (XL_CHART_TYPE.BAR_CLUSTERED, _category_data),
    (XL_CHART_TYPE.BAR_STACKED, _category_data),
    (XL_CHART_TYPE.BAR_STACKED_100, _category_data),
    (XL_CHART_TYPE.COLUMN_CLUSTERED, _category_data),
    (XL_CHART_TYPE.COLUMN_STACKED, _category_data),
    (XL_CHART_TYPE.COLUMN_STACKED_100, _category_data),
    (XL_CHART_TYPE.DOUGHNUT, _category_data),
    (XL_CHART_TYPE.DOUGHNUT_EXPLODED, _category_data),
    (XL_CHART_TYPE.LINE, _category_data),
    (XL_CHART_TYPE.LINE_MARKERS, _category_data),
    (XL_CHART_TYPE.LINE_MARKERS_STACKED, _category_data),
    (XL_CHART_TYPE.LINE_MARKERS_STACKED_100, _category_data),
    (XL_CHART_TYPE.LINE_STACKED, _category_data),
    (XL_CHART_TYPE.LINE_STACKED_100, _category_data),
    (XL_CHART_TYPE.PIE, _category_data),
    (XL_CHART_TYPE.PIE_EXPLODED, _category_data),
    (XL_CHART_TYPE.RADAR, _category_data),
    (XL_CHART_TYPE.RADAR_FILLED, _category_data),
    (XL_CHART_TYPE.RADAR_MARKERS, _category_data),
    (XL_CHART_TYPE.XY_SCATTER, _xy_data),
    (XL_CHART_TYPE.XY_SCATTER_LINES, _xy_data),
    (XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, _xy_data),
    (XL_CHART_TYPE.XY_SCATTER_SMOOTH, _xy_data),
    (XL_CHART_TYPE.XY_SCATTER_SMOOTH_NO_MARKERS, _xy_data),
    (XL_CHART_TYPE.BUBBLE, _bubble_data),
    (XL_CHART_TYPE.BUBBLE_THREE_D_EFFECT, _bubble_data),
]


@pytest.mark.parametrize(
    ("chart_type", "data_factory"),
    CHART_XML_CASES,
    ids=[f"{chart_type.name} ({chart_type.value})" for chart_type, _ in CHART_XML_CASES],
)
def test_chart_xml_writer_matrix(
    chart_type: XL_CHART_TYPE,
    data_factory: Callable[[], object],
    snapshot: SnapshotAssertion,
) -> None:
    chart_data = data_factory()

    xml = ChartXmlWriter(chart_type, chart_data).xml

    assert xml == snapshot(name=chart_type.name)


@pytest.mark.parametrize(
    ("chart_type", "expected_cls"),
    [
        (XL_CHART_TYPE.BAR_CLUSTERED, "_CategorySeriesXmlRewriter"),
        (XL_CHART_TYPE.XY_SCATTER, "_XySeriesXmlRewriter"),
        (XL_CHART_TYPE.BUBBLE, "_BubbleSeriesXmlRewriter"),
    ],
)
def test_series_xml_rewriter_factory(chart_type: XL_CHART_TYPE, expected_cls: str) -> None:
    if chart_type is XL_CHART_TYPE.BUBBLE:
        chart_data = make_bubble_chart_data(1, 2)
    elif chart_type is XL_CHART_TYPE.XY_SCATTER:
        chart_data = make_xy_chart_data(1, 2)
    else:
        chart_data = make_category_chart_data(2, str, 1)

    rewriter = SeriesXmlRewriterFactory(chart_type, chart_data)

    assert rewriter.__class__.__name__ == expected_cls


def test_series_xml_rewriter_replaces_data(snapshot: SnapshotAssertion) -> None:
    chart_data = make_category_chart_data(2, str, 1)
    chart_space_elm = chart_space(
        b"<c:chart><c:plotArea><c:barChart>"
        b"<c:ser><c:idx val='0'/><c:order val='0'/><c:tx><c:strRef><c:strCache><c:pt idx='0'><c:v>Old</c:v></c:pt></c:strCache></c:strRef></c:tx></c:ser>"
        b"</c:barChart></c:plotArea></c:chart>"
    )

    rewriter = SeriesXmlRewriterFactory(XL_CHART_TYPE.BAR_CLUSTERED, chart_data)
    rewriter.replace_series_data(chart_space_elm)

    assert serialize_xml(chart_space_elm) == snapshot
