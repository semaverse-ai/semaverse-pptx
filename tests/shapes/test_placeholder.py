from __future__ import annotations

from pathlib import Path

from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.oxml import parse_xml
from pptx.shapes.placeholder import (
    BasePlaceholder,
    ChartPlaceholder,
    LayoutPlaceholder,
    PicturePlaceholder,
    TablePlaceholder,
    _BaseSlidePlaceholder,
)


def test_base_slide_placeholder_shape_type_and_flag(parent) -> None:
    placeholder = _BaseSlidePlaceholder(
        parse_xml(
            b"""
            <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvSpPr>
                <p:cNvPr id="2" name="Title 1"/>
                <p:cNvSpPr/>
                <p:nvPr><p:ph type="title" idx="0"/></p:nvPr>
              </p:nvSpPr>
              <p:spPr/>
            </p:sp>
            """
        ),
        parent,
    )

    assert placeholder.shape_type == MSO_SHAPE_TYPE.PLACEHOLDER
    assert placeholder.is_placeholder is True


def test_base_slide_placeholder_inherits_dimensions(parent, slide_layout_part) -> None:
    layout_placeholder = parse_xml(
        b"""
        <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:nvSpPr>
            <p:cNvPr id="11" name="Layout Placeholder"/>
            <p:cNvSpPr/>
            <p:nvPr><p:ph type="body" idx="1"/></p:nvPr>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm>
              <a:off x="100" y="200"/>
              <a:ext cx="300" cy="400"/>
            </a:xfrm>
          </p:spPr>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
        </p:sp>
        """
    )
    slide_layout_part._element.cSld.spTree.append(layout_placeholder)

    placeholder = _BaseSlidePlaceholder(
        parse_xml(
            b"""
            <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvSpPr>
                <p:cNvPr id="2" name="Body 1"/>
                <p:cNvSpPr/>
                <p:nvPr><p:ph type="body" idx="1"/></p:nvPr>
              </p:nvSpPr>
              <p:spPr/>
              <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
            </p:sp>
            """
        ),
        parent,
    )

    assert placeholder.left == 100
    assert placeholder.top == 200
    assert placeholder.width == 300
    assert placeholder.height == 400


def test_base_slide_placeholder_overrides_dimensions(parent) -> None:
    placeholder = _BaseSlidePlaceholder(
        parse_xml(
            b"""
            <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvSpPr>
                <p:cNvPr id="2" name="Body 1"/>
                <p:cNvSpPr/>
                <p:nvPr><p:ph type="body" idx="1"/></p:nvPr>
              </p:nvSpPr>
              <p:spPr>
                <a:xfrm>
                  <a:off x="1" y="2"/>
                  <a:ext cx="3" cy="4"/>
                </a:xfrm>
              </p:spPr>
              <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
            </p:sp>
            """
        ),
        parent,
    )

    placeholder.left = 10
    placeholder.top = 20
    placeholder.width = 30
    placeholder.height = 40

    assert placeholder.left == 10
    assert placeholder.top == 20
    assert placeholder.width == 30
    assert placeholder.height == 40


def test_base_placeholder_properties(parent) -> None:
    placeholder = BasePlaceholder(
        parse_xml(
            b"""
            <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvSpPr>
                <p:cNvPr id="2" name="Body 1"/>
                <p:cNvSpPr/>
                <p:nvPr><p:ph type="body" idx="1" orient="vert" sz="half"/></p:nvPr>
              </p:nvSpPr>
              <p:spPr/>
              <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
            </p:sp>
            """
        ),
        parent,
    )

    assert placeholder.idx == 1
    assert placeholder.ph_type == PP_PLACEHOLDER.BODY
    assert placeholder.orient == "vert"
    assert placeholder.sz == "half"


def test_layout_placeholder_resolves_master_base(parent, slide_master_part) -> None:
    master_placeholder = parse_xml(
        b"""
        <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:nvSpPr>
            <p:cNvPr id="21" name="Master Body"/>
            <p:cNvSpPr/>
            <p:nvPr><p:ph type="body" idx="1"/></p:nvPr>
          </p:nvSpPr>
          <p:spPr/>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
        </p:sp>
        """
    )
    slide_master_part._element.cSld.spTree.append(master_placeholder)

    layout_placeholder = LayoutPlaceholder(
        parse_xml(
            b"""
            <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvSpPr>
                <p:cNvPr id="31" name="Layout Chart"/>
                <p:cNvSpPr/>
                <p:nvPr><p:ph type="chart" idx="1"/></p:nvPr>
              </p:nvSpPr>
              <p:spPr/>
              <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
            </p:sp>
            """
        ),
        parent.part.slide_layout,
    )

    assert layout_placeholder._base_placeholder is not None


def test_chart_placeholder_insert_chart(parent) -> None:
    sp = parse_xml(
        b"""
        <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:nvSpPr>
            <p:cNvPr id="42" name="Chart Placeholder 1"/>
            <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
            <p:nvPr><p:ph type="chart" idx="1"/></p:nvPr>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="100" y="200"/><a:ext cx="300" cy="400"/></a:xfrm>
          </p:spPr>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
        </p:sp>
        """
    )
    parent.part._element.cSld.spTree.append(sp)

    placeholder = ChartPlaceholder(sp, parent)
    chart_data = CategoryChartData()
    chart_data.categories = ("Foo", "Bar")
    chart_data.add_series("Series 1", (1, 2))

    graphic_frame = placeholder.insert_chart(XL_CHART_TYPE.PIE, chart_data)

    assert graphic_frame.has_chart is True
    assert parent.part._element.cSld.spTree[-1].tag.endswith("graphicFrame")


def test_picture_placeholder_insert_picture(parent, test_files_dir: Path) -> None:
    sp = parse_xml(
        b"""
        <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:nvSpPr>
            <p:cNvPr id="42" name="Picture Placeholder 1"/>
            <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
            <p:nvPr><p:ph type="pic" idx="1"/></p:nvPr>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="100" y="200"/><a:ext cx="300" cy="400"/></a:xfrm>
          </p:spPr>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
        </p:sp>
        """
    )
    parent.part._element.cSld.spTree.append(sp)

    placeholder = PicturePlaceholder(sp, parent)
    picture = placeholder.insert_picture(str(test_files_dir / "python-icon.jpeg"))

    assert picture.shape_type == MSO_SHAPE_TYPE.PLACEHOLDER
    assert parent.part._element.cSld.spTree[-1].tag.endswith("pic")


def test_table_placeholder_insert_table(parent) -> None:
    sp = parse_xml(
        b"""
        <p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
              xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:nvSpPr>
            <p:cNvPr id="42" name="Table Placeholder 1"/>
            <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
            <p:nvPr><p:ph type="tbl" idx="1"/></p:nvPr>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="100" y="200"/><a:ext cx="300" cy="400"/></a:xfrm>
          </p:spPr>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
        </p:sp>
        """
    )
    parent.part._element.cSld.spTree.append(sp)

    placeholder = TablePlaceholder(sp, parent)
    graphic_frame = placeholder.insert_table(2, 3)

    assert graphic_frame.has_table is True
    assert parent.part._element.cSld.spTree[-1].tag.endswith("graphicFrame")
