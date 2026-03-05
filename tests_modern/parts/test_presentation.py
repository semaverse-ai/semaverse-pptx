from __future__ import annotations

from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.packuri import PackURI
from pptx.oxml import parse_xml
from pptx.package import Package
from pptx.parts.presentation import PresentationPart
from pptx.parts.slide import SlideLayoutPart, SlidePart
from pptx.slide import SlideLayout

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _presentation_xml(with_sld_id_list: bool = False) -> bytes:
    sld_id_list_xml = "<p:sldIdLst/>" if with_sld_id_list else ""
    xml = f'<p:presentation xmlns:p="{P_NS}">{sld_id_list_xml}</p:presentation>'
    return xml.encode("utf-8")


def _slide_xml() -> bytes:
    return f'<p:sld xmlns:p="{P_NS}"/>'.encode("utf-8")


def _slide_layout_xml() -> bytes:
    xml = f'<p:sldLayout xmlns:p="{P_NS}"><p:cSld><p:spTree/></p:cSld></p:sldLayout>'
    return xml.encode("utf-8")


def test_presentation_part_access_presentation() -> None:
    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        None,
        parse_xml(_presentation_xml()),
    )

    assert part.presentation is not None


def test_presentation_part_rename_slide_parts() -> None:
    pkg = Package(None)
    prs_part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        pkg,
        parse_xml(_presentation_xml()),
    )

    slide_parts = [
        SlidePart(PackURI("/ppt/slides/slide99.xml"), CT.PML_SLIDE, pkg, parse_xml(_slide_xml()))
        for _ in range(3)
    ]
    r_ids: list[str] = []
    for slide_part in slide_parts:
        r_ids.append(
            prs_part.relate_to(
                slide_part,
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
            )
        )

    prs_part.rename_slide_parts(r_ids)

    assert slide_parts[0].partname == "/ppt/slides/slide1.xml"
    assert slide_parts[1].partname == "/ppt/slides/slide2.xml"
    assert slide_parts[2].partname == "/ppt/slides/slide3.xml"


def test_presentation_part_add_slide() -> None:
    pkg = Package(None)
    prs_part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        pkg,
        parse_xml(_presentation_xml(with_sld_id_list=True)),
    )

    layout_part = SlideLayoutPart(
        PackURI("/ppt/slideLayouts/slideLayout1.xml"),
        CT.PML_SLIDE_LAYOUT,
        pkg,
        parse_xml(_slide_layout_xml()),
    )
    layout = SlideLayout(layout_part._element, layout_part)

    rId, slide = prs_part.add_slide(layout)

    assert slide.slide_layout == layout
    assert rId in prs_part.rels
