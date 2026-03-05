from __future__ import annotations

from datetime import date
from itertools import islice
from typing import Type, Union

from pptx.chart.data import BubbleChartData, CategoryChartData, XyChartData
from pptx.oxml import parse_xml

CategoryType = Union[Type[str], Type[float], Type[date]]


def chart_space(xml_body: bytes) -> object:
    return parse_xml(
        b'<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
        b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        b'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        + xml_body
        + b"</c:chartSpace>"
    )


def make_category_chart_data(
    cat_count: int,
    cat_type: CategoryType = str,
    ser_count: int = 2,
) -> CategoryChartData:
    labels = {
        str: ("Foo", "Bar", "Baz", "Boo", "Far", "Faz"),
        float: (1.1, 2.2, 3.3, 4.4, 5.5, 6.6),
        date: (
            date(2016, 12, 27),
            date(2016, 12, 28),
            date(2016, 12, 29),
            date(2016, 12, 30),
            date(2016, 12, 31),
            date(2017, 1, 1),
        ),
    }[cat_type]

    point_values = (round((x * 1.1), 1) for x in range(1, 100))

    chart_data = CategoryChartData()
    chart_data.categories = labels[:cat_count]

    for idx in range(ser_count):
        series_values = tuple(islice(point_values, cat_count))
        chart_data.add_series(f"Series {idx + 1}", series_values)

    return chart_data


def make_xy_chart_data(ser_count: int = 2, point_count: int = 3) -> XyChartData:
    points = (
        (1.1, 11.1),
        (2.1, 12.1),
        (3.1, 13.1),
        (1.2, 11.2),
        (2.2, 12.2),
        (3.2, 13.2),
    )

    chart_data = XyChartData()
    for i in range(ser_count):
        series = chart_data.add_series(f"Series {i + 1}")
        for j in range(point_count):
            x, y = points[i * point_count + j]
            series.add_data_point(x, y)

    return chart_data


def make_bubble_chart_data(ser_count: int = 2, point_count: int = 3) -> BubbleChartData:
    points = (
        (1.1, 11.1, 10.0),
        (2.1, 12.1, 20.0),
        (3.1, 13.1, 30.0),
        (1.2, 11.2, 40.0),
        (2.2, 12.2, 50.0),
        (3.2, 13.2, 60.0),
    )

    chart_data = BubbleChartData()
    for i in range(ser_count):
        series = chart_data.add_series(f"Series {i + 1}")
        for j in range(point_count):
            x, y, size = points[i * point_count + j]
            series.add_data_point(x, y, size)

    return chart_data
