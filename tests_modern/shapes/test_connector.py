from __future__ import annotations

from syrupy.assertion import SnapshotAssertion

from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml import parse_xml
from pptx.shapes.autoshape import Shape
from pptx.shapes.connector import Connector


def _shape_for_connection(parent) -> Shape:
    return Shape(
        parse_xml(
            b"""
            <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvSpPr>
                <p:cNvPr id="77" name="Target"/>
                <p:cNvSpPr/>
                <p:nvPr/>
              </p:nvSpPr>
              <p:spPr>
                <a:xfrm>
                  <a:off x="100" y="200"/>
                  <a:ext cx="300" cy="400"/>
                </a:xfrm>
                <a:prstGeom prst="rect"/>
              </p:spPr>
              <p:txBody>
                <a:bodyPr/>
                <a:lstStyle/>
                <a:p/>
              </p:txBody>
            </p:sp>
            """
        ),
        parent,
    )


def test_connector_point_properties(parent) -> None:
    connector = Connector(
        parse_xml(
            b"""
            <p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                     xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvCxnSpPr>
                <p:cNvPr id="42" name="Connector 1"/>
                <p:cNvCxnSpPr/>
                <p:nvPr/>
              </p:nvCxnSpPr>
              <p:spPr>
                <a:xfrm>
                  <a:off x="100" y="200"/>
                  <a:ext cx="300" cy="400"/>
                </a:xfrm>
              </p:spPr>
            </p:cxnSp>
            """
        ),
        parent,
    )

    assert connector.begin_x == 100
    assert connector.begin_y == 200
    assert connector.end_x == 400
    assert connector.end_y == 600

    connector.begin_x = 150
    connector.begin_y = 250
    connector.end_x = 500
    connector.end_y = 700

    assert connector.begin_x == 150
    assert connector.begin_y == 250
    assert connector.end_x == 500
    assert connector.end_y == 700


def test_connector_connectors_add_st_cxn_and_end_cxn(parent, snapshot: SnapshotAssertion) -> None:
    connector = Connector(
        parse_xml(
            b"""
            <p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                     xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvCxnSpPr>
                <p:cNvPr id="42" name="Connector 1"/>
                <p:cNvCxnSpPr/>
                <p:nvPr/>
              </p:nvCxnSpPr>
              <p:spPr>
                <a:xfrm>
                  <a:off x="10" y="20"/>
                  <a:ext cx="30" cy="40"/>
                </a:xfrm>
              </p:spPr>
            </p:cxnSp>
            """
        ),
        parent,
    )
    shape = _shape_for_connection(parent)

    connector.begin_connect(shape, 0)
    connector.end_connect(shape, 2)

    assert connector.begin_x == 250
    assert connector.begin_y == 200
    assert connector.end_x == 250
    assert connector.end_y == 600
    assert snapshot == connector._element.xml


def test_connector_line_and_shape_type(parent) -> None:
    connector = Connector(
        parse_xml(
            b"""
            <p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                     xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvCxnSpPr>
                <p:cNvPr id="42" name="Connector 1"/>
                <p:cNvCxnSpPr/>
                <p:nvPr/>
              </p:nvCxnSpPr>
              <p:spPr>
                <a:xfrm>
                  <a:off x="100" y="200"/>
                  <a:ext cx="300" cy="400"/>
                </a:xfrm>
              </p:spPr>
            </p:cxnSp>
            """
        ),
        parent,
    )

    connector.line.width = 12700

    assert connector.shape_type == MSO_SHAPE_TYPE.LINE
    assert connector.line.width == 12700
