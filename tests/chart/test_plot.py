from __future__ import annotations

# ruff: noqa: E501
from pptx.chart.plot import BarPlot, BubblePlot, PlotFactory
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml import parse_xml


def test_plot_factory_and_base_properties() -> None:
    plot = PlotFactory(
        parse_xml(
            b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:ser><c:idx val='0'/><c:order val='0'/><c:cat><c:numRef><c:numCache><c:ptCount val='2'/></c:numCache></c:numRef></c:cat></c:ser>"
            b"</c:barChart>"
        ),
        chart=None,
    )

    assert isinstance(plot, BarPlot)
    assert plot.has_data_labels is False
    assert plot.vary_by_categories is True

    plot.has_data_labels = True
    plot.vary_by_categories = False

    assert plot.has_data_labels is True
    assert plot.vary_by_categories is False


def test_bar_plot_gap_width_and_overlap() -> None:
    plot = PlotFactory(
        parse_xml(
            b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:barDir val='bar'/><c:grouping val='clustered'/><c:ser><c:idx val='0'/><c:order val='0'/></c:ser>"
            b"</c:barChart>"
        ),
        chart=None,
    )

    assert plot.gap_width == 150
    assert plot.overlap == 0

    plot.gap_width = 300
    plot.overlap = 42

    assert plot.gap_width == 300
    assert plot.overlap == 42


def test_bubble_plot_scale() -> None:
    plot = PlotFactory(
        parse_xml(
            b'<c:bubbleChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:ser><c:idx val='0'/><c:order val='0'/></c:ser></c:bubbleChart>"
        ),
        chart=None,
    )

    assert isinstance(plot, BubblePlot)
    assert plot.bubble_scale == 100

    plot.bubble_scale = 70

    assert plot.bubble_scale == 70


def test_plot_chart_type_integration() -> None:
    plot = PlotFactory(
        parse_xml(
            b'<c:lineChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            b"<c:grouping val='standard'/><c:ser><c:idx val='0'/><c:order val='0'/></c:ser></c:lineChart>"
        ),
        chart=None,
    )

    assert plot is not None
    assert plot.__class__.__name__ == "LinePlot"
    assert XL_CHART_TYPE.LINE is not None
