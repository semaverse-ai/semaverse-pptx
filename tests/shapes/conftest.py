from __future__ import annotations

from dataclasses import dataclass

import pytest

from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.oxml import parse_xml
from pptx.oxml.slide import CT_Slide
from pptx.package import Package
from pptx.parts.slide import SlideLayoutPart, SlideMasterPart, SlidePart


@dataclass
class ParentProxy:
    part: SlidePart


@pytest.fixture
def package() -> Package:
    return Package(None)


@pytest.fixture
def slide_master_part(package: Package) -> SlideMasterPart:
    xml = parse_xml(
        b"""
        <p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                     xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:cSld>
            <p:spTree>
              <p:nvGrpSpPr>
                <p:cNvPr id="1" name=""/>
                <p:cNvGrpSpPr/>
                <p:nvPr/>
              </p:nvGrpSpPr>
              <p:grpSpPr>
                <a:xfrm>
                  <a:off x="0" y="0"/>
                  <a:ext cx="0" cy="0"/>
                  <a:chOff x="0" y="0"/>
                  <a:chExt cx="0" cy="0"/>
                </a:xfrm>
              </p:grpSpPr>
            </p:spTree>
          </p:cSld>
        </p:sldMaster>
        """
    )
    return SlideMasterPart(
        PackURI("/ppt/slideMasters/slideMaster1.xml"),
        CT.PML_SLIDE_MASTER,
        package,
        xml,
    )


@pytest.fixture
def slide_layout_part(package: Package, slide_master_part: SlideMasterPart) -> SlideLayoutPart:
    xml = parse_xml(
        b"""
        <p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                     xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <p:cSld>
            <p:spTree>
              <p:nvGrpSpPr>
                <p:cNvPr id="1" name=""/>
                <p:cNvGrpSpPr/>
                <p:nvPr/>
              </p:nvGrpSpPr>
              <p:grpSpPr>
                <a:xfrm>
                  <a:off x="0" y="0"/>
                  <a:ext cx="0" cy="0"/>
                  <a:chOff x="0" y="0"/>
                  <a:chExt cx="0" cy="0"/>
                </a:xfrm>
              </p:grpSpPr>
            </p:spTree>
          </p:cSld>
        </p:sldLayout>
        """
    )
    layout = SlideLayoutPart(
        PackURI("/ppt/slideLayouts/slideLayout1.xml"),
        CT.PML_SLIDE_LAYOUT,
        package,
        xml,
    )
    layout.relate_to(slide_master_part, RT.SLIDE_MASTER)
    return layout


@pytest.fixture
def slide_part(package: Package, slide_layout_part: SlideLayoutPart) -> SlidePart:
    part = SlidePart(PackURI("/ppt/slides/slide1.xml"), CT.PML_SLIDE, package, CT_Slide.new())
    part.relate_to(slide_layout_part, RT.SLIDE_LAYOUT)
    return part


@pytest.fixture
def parent(slide_part: SlidePart) -> ParentProxy:
    return ParentProxy(slide_part)
