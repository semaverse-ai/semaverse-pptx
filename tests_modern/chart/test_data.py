from __future__ import annotations

from datetime import date

from pptx.chart.data import BubbleChartData, CategoryChartData, ChartData, XyChartData
from pptx.enum.chart import XL_CHART_TYPE


def test_chart_data_alias() -> None:
    assert isinstance(ChartData(), CategoryChartData)


def test_category_chart_data_properties() -> None:
    chart_data = CategoryChartData(number_format="0.0")

    assert chart_data.number_format == "0.0"

    chart_data.categories = ("A", "B", "C")
    series = chart_data.add_series("Series 1", (1, 2, 3), number_format="0.00")

    assert len(chart_data) == 1
    assert series.name == "Series 1"
    assert series.values == [1, 2, 3]
    assert series.number_format == "0.00"
    assert chart_data.categories_ref.startswith("Sheet1!")
    assert chart_data.values_ref(series).startswith("Sheet1!")


def test_category_chart_data_date_categories() -> None:
    chart_data = CategoryChartData()
    chart_data.categories = (date(2020, 1, 1), date(2020, 1, 2))
    chart_data.add_series("Series 1", (10, 20))

    assert chart_data.categories.are_dates is True
    assert chart_data.categories.are_numeric is True


def test_xy_chart_data() -> None:
    chart_data = XyChartData()
    series = chart_data.add_series("Series 1")
    series.add_data_point(1, 2)
    series.add_data_point(3, 4)

    assert len(series) == 2
    assert series.x_values == [1, 3]
    assert series.y_values == [2, 4]


def test_bubble_chart_data() -> None:
    chart_data = BubbleChartData()
    series = chart_data.add_series("Series 1")
    series.add_data_point(1, 2, 10)
    series.add_data_point(3, 4, 20)

    assert len(series) == 2
    assert series.x_values == [1, 3]
    assert series.y_values == [2, 4]
    assert series.bubble_sizes == [10, 20]


def test_chart_data_xml_bytes() -> None:
    chart_data = CategoryChartData()
    chart_data.categories = ("A", "B")
    chart_data.add_series("Series 1", (1, 2))

    xml_bytes = chart_data.xml_bytes(XL_CHART_TYPE.BAR_CLUSTERED)

    assert xml_bytes.startswith(b"<?xml")
    assert b"<c:chartSpace" in xml_bytes
