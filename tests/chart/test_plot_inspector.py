from __future__ import annotations

import pytest

from pptx.chart.plot import PlotFactory, PlotTypeInspector
from pptx.enum.chart import XL_CHART_TYPE as XL
from pptx.oxml import parse_xml


def _plot(xml: bytes):
    return PlotFactory(parse_xml(xml), chart="chart-proxy")


def test_base_plot_chart_categories_series_and_data_labels() -> None:
    plot = _plot(
        b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:ser>"
        b"<c:idx val='0'/><c:order val='0'/>"
        b"<c:cat><c:strRef><c:strCache><c:ptCount val='2'/>"
        b"<c:pt idx='0'><c:v>A</c:v></c:pt>"
        b"<c:pt idx='1'><c:v>B</c:v></c:pt>"
        b"</c:strCache></c:strRef></c:cat>"
        b"</c:ser>"
        b"</c:barChart>"
    )

    categories = plot.categories
    series = plot.series
    chart = plot.chart

    assert chart == "chart-proxy"
    assert len(categories) == 2
    assert len(series) == 1
    with pytest.raises(ValueError, match="plot has no data labels"):
        _ = plot.data_labels


def test_base_plot_data_labels_and_vary_colors_setter_paths() -> None:
    plot = _plot(
        b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:ser><c:idx val='0'/><c:order val='0'/></c:ser>"
        b"<c:dLbls><c:showVal val='0'/></c:dLbls>"
        b"<c:varyColors val='0'/>"
        b"</c:barChart>"
    )

    labels = plot.data_labels
    plot.has_data_labels = False
    plot.has_data_labels = True
    plot.vary_by_categories = True

    assert labels is not None
    assert plot.has_data_labels is True
    assert plot._element.dLbls.showVal.val is True
    assert plot.vary_by_categories is True


def test_bar_plot_overlap_zero_removes_overlap_element() -> None:
    plot = _plot(
        b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:barDir val='bar'/><c:grouping val='clustered'/>"
        b"<c:overlap val='42'/>"
        b"<c:ser><c:idx val='0'/><c:order val='0'/></c:ser>"
        b"</c:barChart>"
    )

    plot.overlap = 0

    assert plot._element.overlap is None


def test_bubble_plot_bubble_scale_none_removes_override() -> None:
    plot = _plot(
        b'<c:bubbleChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:bubbleScale val='120'/>"
        b"<c:ser><c:idx val='0'/><c:order val='0'/></c:ser>"
        b"</c:bubbleChart>"
    )

    plot.bubble_scale = None

    assert plot._element.bubbleScale is None


def test_plot_factory_raises_for_unsupported_plot() -> None:
    xml = b'<c:surfaceChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"/>'

    # Act / Assert
    with pytest.raises(ValueError, match="unsupported plot type"):
        PlotFactory(parse_xml(xml), chart=None)


@pytest.mark.parametrize(
    ("xml", "expected"),
    [
        (
            b'<c:areaChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:grouping val='stacked'/>"
            b"</c:areaChart>",
            XL.AREA_STACKED,
        ),
        (
            b'<c:area3DChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:grouping val='percentStacked'/>"
            b"</c:area3DChart>",
            XL.THREE_D_AREA_STACKED_100,
        ),
        (
            b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:barDir val='bar'/><c:grouping val='clustered'/>"
            b"</c:barChart>",
            XL.BAR_CLUSTERED,
        ),
        (
            b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:barDir val='col'/><c:grouping val='stacked'/>"
            b"</c:barChart>",
            XL.COLUMN_STACKED,
        ),
        (
            b'<c:bubbleChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:ser><c:bubble3D val='1'/></c:ser>"
            b"</c:bubbleChart>",
            XL.BUBBLE_THREE_D_EFFECT,
        ),
        (
            b'<c:doughnutChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:ser><c:explosion val='5'/></c:ser>"
            b"</c:doughnutChart>",
            XL.DOUGHNUT_EXPLODED,
        ),
        (
            b'<c:lineChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:grouping val='percentStacked'/>"
            b"<c:ser><c:marker><c:symbol val='none'/></c:marker></c:ser>"
            b"</c:lineChart>",
            XL.LINE_STACKED_100,
        ),
        (
            b'<c:pieChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:ser/>"
            b"</c:pieChart>",
            XL.PIE,
        ),
        (
            b'<c:radarChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:radarStyle val='filled'/>"
            b"</c:radarChart>",
            XL.RADAR_FILLED,
        ),
        (
            b'<c:scatterChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
            b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            b"<c:scatterStyle val='smoothMarker'/>"
            b"<c:ser><c:marker><c:symbol val='none'/></c:marker></c:ser>"
            b"</c:scatterChart>",
            XL.XY_SCATTER_SMOOTH_NO_MARKERS,
        ),
    ],
)
def test_plot_type_inspector_chart_type(xml: bytes, expected: XL) -> None:
    plot = _plot(xml)

    chart_type = PlotTypeInspector.chart_type(plot)

    assert chart_type == expected


def test_plot_type_inspector_raises_for_unknown_plot_class() -> None:
    class UnknownPlot:
        pass

    # Act / Assert
    with pytest.raises(NotImplementedError, match="chart_type\\(\\) not implemented"):
        PlotTypeInspector.chart_type(UnknownPlot())


def test_plot_type_inspector_invalid_bar_dir_raises() -> None:
    plot = _plot(
        b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:barDir val='diag'/><c:grouping val='clustered'/>"
        b"</c:barChart>"
    )

    # Act / Assert
    with pytest.raises(ValueError, match="invalid barChart.barDir value"):
        PlotTypeInspector.chart_type(plot)


def test_plot_type_inspector_radar_default_and_no_marker_paths() -> None:
    default_plot = _plot(
        b'<c:radarChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:radarStyle/>"
        b"</c:radarChart>"
    )
    no_marker_plot = _plot(
        b'<c:radarChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:radarStyle val='marker'/>"
        b"<c:ser><c:marker><c:symbol val='none'/></c:marker></c:ser>"
        b"</c:radarChart>"
    )

    # Act / Assert
    assert PlotTypeInspector.chart_type(default_plot) == XL.RADAR
    assert PlotTypeInspector.chart_type(no_marker_plot) == XL.RADAR


def test_plot_type_inspector_xy_line_marker_variants() -> None:
    no_line_plot = _plot(
        b'<c:scatterChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
        b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        b"<c:scatterStyle val='lineMarker'/>"
        b"<c:ser><c:spPr><a:ln><a:noFill/></a:ln></c:spPr></c:ser>"
        b"</c:scatterChart>"
    )
    no_markers_plot = _plot(
        b'<c:scatterChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:scatterStyle val='lineMarker'/>"
        b"<c:ser><c:marker><c:symbol val='none'/></c:marker></c:ser>"
        b"</c:scatterChart>"
    )
    with_markers_plot = _plot(
        b'<c:scatterChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:scatterStyle val='lineMarker'/>"
        b"<c:ser><c:marker><c:symbol val='circle'/></c:marker></c:ser>"
        b"</c:scatterChart>"
    )

    # Act / Assert
    assert PlotTypeInspector.chart_type(no_line_plot) == XL.XY_SCATTER
    assert PlotTypeInspector.chart_type(no_markers_plot) == XL.XY_SCATTER_LINES_NO_MARKERS
    assert PlotTypeInspector.chart_type(with_markers_plot) == XL.XY_SCATTER_LINES
