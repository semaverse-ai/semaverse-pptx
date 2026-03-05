from __future__ import annotations

import io
import zipfile

import pytest
from lxml import etree
from syrupy.assertion import SnapshotAssertion

from pptx.chart.data import BubbleChartData, CategoryChartData, XyChartData
from pptx.chart.xlsx import BubbleWorkbookWriter, CategoryWorkbookWriter, XyWorkbookWriter
from tests.xml_utils import serialize_xml


def _member_xml(blob: bytes, member_name: str) -> str:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        xml_bytes = zf.read(member_name)

    element = etree.fromstring(xml_bytes)
    return serialize_xml(element)


def test_category_workbook_writer_refs() -> None:
    data = CategoryChartData()
    data.categories = ("A", "B")
    series = data.add_series("Series 1", (1, 2))
    writer = CategoryWorkbookWriter(data)

    assert writer.categories_ref == "Sheet1!$A$2:$A$3"
    assert writer.series_name_ref(series) == "Sheet1!$B$1"
    assert writer.values_ref(series) == "Sheet1!$B$2:$B$3"


def test_column_reference_bounds() -> None:
    assert CategoryWorkbookWriter._column_reference(1) == "A"
    assert CategoryWorkbookWriter._column_reference(26) == "Z"
    assert CategoryWorkbookWriter._column_reference(27) == "AA"

    with pytest.raises(ValueError):
        CategoryWorkbookWriter._column_reference(0)


def test_category_workbook_writer_sheet_xml(snapshot: SnapshotAssertion) -> None:
    data = CategoryChartData()
    data.categories = ("A", "B")
    data.add_series("Series 1", (1.1, 2.2))

    sheet_xml = _member_xml(CategoryWorkbookWriter(data).xlsx_blob, "xl/worksheets/sheet1.xml")

    assert sheet_xml == snapshot


def test_xy_workbook_writer_sheet_xml(snapshot: SnapshotAssertion) -> None:
    data = XyChartData()
    series = data.add_series("Series 1")
    series.add_data_point(1.1, 2.2)
    series.add_data_point(3.3, 4.4)

    sheet_xml = _member_xml(XyWorkbookWriter(data).xlsx_blob, "xl/worksheets/sheet1.xml")

    assert sheet_xml == snapshot


def test_bubble_workbook_writer_sheet_xml(snapshot: SnapshotAssertion) -> None:
    data = BubbleChartData()
    series = data.add_series("Series 1")
    series.add_data_point(1.1, 2.2, 10)
    series.add_data_point(3.3, 4.4, 20)

    writer = BubbleWorkbookWriter(data)
    sheet_xml = _member_xml(writer.xlsx_blob, "xl/worksheets/sheet1.xml")

    assert writer.bubble_sizes_ref(series) == "Sheet1!$C$2:$C$3"
    assert sheet_xml == snapshot
