from __future__ import annotations

import io

from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.packuri import PackURI
from pptx.oxml import parse_xml
from pptx.package import Package
from pptx.parts.slide import NotesMasterPart, SlideLayoutPart, SlidePart


def test_base_slide_part_name() -> None:
    xml = (
        b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        b'<p:cSld name="Slide 1"/></p:sld>'
    )

    part = SlidePart(PackURI("/ppt/slides/slide1.xml"), CT.PML_SLIDE, None, parse_xml(xml))

    assert part.name == "Slide 1"


def test_notes_master_part_create_default() -> None:
    pkg = Package(None)

    part = NotesMasterPart.create_default(pkg)

    assert isinstance(part, NotesMasterPart)
    assert part.partname == "/ppt/notesMasters/notesMaster1.xml"
    assert part.notes_master is not None


def test_slide_part_new() -> None:
    pkg = Package(None)
    layout_part = SlideLayoutPart(
        PackURI("/ppt/slideLayouts/slideLayout1.xml"),
        CT.PML_SLIDE_LAYOUT,
        pkg,
        parse_xml(b'<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )

    part = SlidePart.new(PackURI("/ppt/slides/slide1.xml"), pkg, layout_part)

    assert isinstance(part, SlidePart)
    assert part.partname == "/ppt/slides/slide1.xml"
    assert part.slide_layout is layout_part.slide_layout


def test_slide_part_add_embedded_ole_object_part() -> None:
    pkg = Package(None)
    part = SlidePart(
        PackURI("/ppt/slides/slide1.xml"),
        CT.PML_SLIDE,
        pkg,
        parse_xml(b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )

    rId = part.add_embedded_ole_object_part("Excel.Sheet.12", io.BytesIO(b"xls_data"))

    related = part.related_part(rId)

    assert related.blob == b"xls_data"
