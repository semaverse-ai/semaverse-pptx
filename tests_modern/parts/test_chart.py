from __future__ import annotations

from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE as XCT
from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.package import Package
from pptx.parts.chart import ChartPart


def test_chart_part_new() -> None:
    pkg = Package(None)
    chart_data = CategoryChartData()
    chart_data.categories = ("A", "B")
    chart_data.add_series("Series 1", (1, 2))

    part = ChartPart.new(XCT.BAR_CLUSTERED, chart_data, pkg)

    assert isinstance(part, ChartPart)
    assert part.content_type == CT.DML_CHART
    assert part.partname.startswith("/ppt/charts/chart")
    assert b"c:chartSpace" in part.blob


def test_chart_workbook_update_xlsx() -> None:
    pkg = Package(None)
    chart_data = CategoryChartData()
    chart_data.categories = ("A", "B")
    chart_data.add_series("Series 1", (1, 2))

    part = ChartPart.new(XCT.BAR_CLUSTERED, chart_data, pkg)
    workbook = part.chart_workbook

    old_blob = workbook.xlsx_part.blob

    chart_data.add_series("Series 2", (3, 4))
    workbook.update_from_xlsx_blob(chart_data.xlsx_blob)

    assert workbook.xlsx_part.blob != old_blob
    assert len(workbook.xlsx_part.blob) > 0
