from __future__ import annotations

from pptx.oxml import parse_xml
from pptx.oxml.shapes.graphfrm import CT_GraphicalObjectFrame
from pptx.spec import GRAPHIC_DATA_URI_CHART, GRAPHIC_DATA_URI_OLEOBJ, GRAPHIC_DATA_URI_TABLE


def test_graphic_frame_new_graphic_frame() -> None:
    graphic_frame = CT_GraphicalObjectFrame.new_graphicFrame(42, "foobar", 1, 2, 3, 4)

    assert graphic_frame.nvGraphicFramePr.cNvPr.id == 42
    assert graphic_frame.nvGraphicFramePr.cNvPr.name == "foobar"
    assert graphic_frame.x == 1
    assert graphic_frame.y == 2


def test_graphic_frame_new_chart_graphic_frame() -> None:
    graphic_frame = CT_GraphicalObjectFrame.new_chart_graphicFrame(42, "foobar", "rId6", 1, 2, 3, 4)

    assert graphic_frame.graphicData.uri == GRAPHIC_DATA_URI_CHART
    assert graphic_frame.chart_rId == "rId6"


def test_graphic_frame_new_table_graphic_frame() -> None:
    graphic_frame = CT_GraphicalObjectFrame.new_table_graphicFrame(42, "foobar", 2, 3, 1, 2, 3, 4)

    assert graphic_frame.graphicData.uri == GRAPHIC_DATA_URI_TABLE


def test_graphic_frame_new_ole_object_graphic_frame() -> None:
    graphic_frame = CT_GraphicalObjectFrame.new_ole_object_graphicFrame(
        42,
        "foobar",
        "rId1",
        "Excel.Sheet.12",
        "rId2",
        1,
        2,
        3,
        4,
        10,
        20,
    )

    assert graphic_frame.graphicData.uri == GRAPHIC_DATA_URI_OLEOBJ
    assert graphic_frame.graphicData._oleObj.rId == "rId1"


def test_graphic_frame_chart_properties() -> None:
    graphic_frame = parse_xml(
        '<p:graphicFrame xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        '<c:chart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'r:id="rId42"/></a:graphicData></a:graphic></p:graphicFrame>'
    )

    assert graphic_frame.has_oleobj is False
    assert graphic_frame.is_embedded_ole_obj is None
    assert graphic_frame.chart_rId == "rId42"
    assert graphic_frame.graphicData_uri == "http://schemas.openxmlformats.org/drawingml/2006/chart"
    assert graphic_frame.chart is not None


def test_graphic_frame_ole_properties_embedded() -> None:
    graphic_frame = parse_xml(
        '<p:graphicFrame xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/presentationml/2006/ole">'
        '<p:oleObj r:id="rId42" progId="Excel.Sheet.12" showAsIcon="1"><p:embed/></p:oleObj>'
        "</a:graphicData></a:graphic></p:graphicFrame>"
    )

    assert graphic_frame.has_oleobj is True
    assert graphic_frame.is_embedded_ole_obj is True
    assert graphic_frame.graphicData.blob_rId == "rId42"
    assert graphic_frame.graphicData.progId == "Excel.Sheet.12"
    assert graphic_frame.graphicData.showAsIcon is True


def test_graphic_frame_ole_properties_linked() -> None:
    graphic_frame = parse_xml(
        '<p:graphicFrame xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/presentationml/2006/ole">'
        '<p:oleObj r:id="rId42" progId="Excel.Sheet.12"><p:link/></p:oleObj>'
        "</a:graphicData></a:graphic></p:graphicFrame>"
    )

    assert graphic_frame.has_oleobj is True
    assert graphic_frame.is_embedded_ole_obj is False
    assert graphic_frame.graphicData.showAsIcon is False
