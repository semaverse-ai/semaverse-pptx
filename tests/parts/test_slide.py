from __future__ import annotations

import io

from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.oxml import parse_xml
from pptx.package import Package
from pptx.parts.slide import NotesMasterPart, NotesSlidePart, SlideLayoutPart, SlideMasterPart, SlidePart
from pptx.slide import NotesSlide
from tests.stubs import (
    NotesMasterPartProxy,
    NotesSlideCloneProxy,
    NotesSlidePartProxy,
    PackagePresentationProxy,
    PackageWithPresentationPartProxy,
    PresentationPartNotesMasterProxy,
    SlideIdPresentationPartProxy,
    SlideLayoutPartProxy,
)


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


def test_notes_slide_part_new_clones_master_placeholders(
    monkeypatch,
) -> None:
    notes_master = object()
    notes_slide = NotesSlideCloneProxy()
    notes_slide_part = NotesSlidePartProxy(notes_slide=notes_slide)
    package = PackagePresentationProxy(
        PresentationPartNotesMasterProxy(NotesMasterPartProxy(notes_master))
    )

    monkeypatch.setattr(
        NotesSlidePart,
        "_add_notes_slide_part",
        classmethod(lambda cls, package, slide_part, notes_master_part: notes_slide_part),
    )

    new_part = NotesSlidePart.new(package, slide_part=object())

    assert new_part is notes_slide_part
    assert notes_slide.clone_calls == [notes_master]


def test_notes_slide_part_notes_master_and_notes_slide_properties() -> None:
    xml = parse_xml(
        b'<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree/></p:cSld></p:notes>'
    )
    part = NotesSlidePart(
        PackURI("/ppt/notesSlides/notesSlide1.xml"),
        CT.PML_NOTES_SLIDE,
        Package(None),
        xml,
    )
    expected_notes_master = object()
    part.part_related_by = (  # type: ignore[method-assign]
        lambda reltype: NotesMasterPartProxy(expected_notes_master)
    )

    assert part.notes_master is expected_notes_master
    assert isinstance(part.notes_slide, NotesSlide)


def test_notes_slide_part_add_notes_slide_part_relates_to_master_and_slide() -> None:
    package = Package(None)
    slide_part = SlidePart(
        PackURI("/ppt/slides/slide1.xml"),
        CT.PML_SLIDE,
        package,
        parse_xml(b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )
    notes_master_part = NotesMasterPart.create_default(package)

    notes_slide_part = NotesSlidePart._add_notes_slide_part(package, slide_part, notes_master_part)

    assert notes_slide_part.part_related_by(RT.NOTES_MASTER) is notes_master_part
    assert notes_slide_part.part_related_by(RT.SLIDE) is slide_part


def test_slide_part_has_notes_slide_true_and_false_paths() -> None:
    part = SlidePart(
        PackURI("/ppt/slides/slide1.xml"),
        CT.PML_SLIDE,
        Package(None),
        parse_xml(b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )

    part.part_related_by = lambda reltype: (_ for _ in ()).throw(KeyError())  # type: ignore[method-assign]
    assert part.has_notes_slide is False

    part.part_related_by = lambda reltype: object()  # type: ignore[method-assign]
    assert part.has_notes_slide is True


def test_slide_part_notes_slide_existing_and_create_paths(monkeypatch) -> None:
    notes_xml = parse_xml(
        b'<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree/></p:cSld></p:notes>'
    )
    existing_notes_part = NotesSlidePart(
        PackURI("/ppt/notesSlides/notesSlide1.xml"),
        CT.PML_NOTES_SLIDE,
        Package(None),
        notes_xml,
    )

    existing_notes_slide_part = SlidePart(
        PackURI("/ppt/slides/slide1.xml"),
        CT.PML_SLIDE,
        Package(None),
        parse_xml(b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )
    existing_notes_slide_part.relate_to(existing_notes_part, RT.NOTES_SLIDE)

    assert existing_notes_slide_part.notes_slide is existing_notes_part.notes_slide

    created_notes_slide_part = SlidePart(
        PackURI("/ppt/slides/slide2.xml"),
        CT.PML_SLIDE,
        Package(None),
        parse_xml(b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )
    monkeypatch.setattr(
        SlidePart,
        "_add_notes_slide_part",
        lambda self: existing_notes_part,
    )

    assert created_notes_slide_part.notes_slide is existing_notes_part.notes_slide


def test_slide_part_slide_id_uses_presentation_part() -> None:
    part = SlidePart(
        PackURI("/ppt/slides/slide1.xml"),
        CT.PML_SLIDE,
        PackageWithPresentationPartProxy(SlideIdPresentationPartProxy(987)),
        parse_xml(b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )

    assert part.slide_id == 987


def test_slide_part_add_notes_slide_part_relates_created_part(monkeypatch) -> None:
    package = Package(None)
    part = SlidePart(
        PackURI("/ppt/slides/slide1.xml"),
        CT.PML_SLIDE,
        package,
        parse_xml(b'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'),
    )
    notes_slide_part = NotesSlidePart(
        PackURI("/ppt/notesSlides/notesSlide1.xml"),
        CT.PML_NOTES_SLIDE,
        package,
        parse_xml(
            b'<p:notes xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree/></p:cSld></p:notes>'
        ),
    )
    monkeypatch.setattr(NotesSlidePart, "new", lambda package, slide_part: notes_slide_part)

    added_part = part._add_notes_slide_part()

    assert added_part is notes_slide_part
    assert part.part_related_by(RT.NOTES_SLIDE) is notes_slide_part


def test_slide_master_part_related_slide_layout() -> None:
    part = SlideMasterPart(
        PackURI("/ppt/slideMasters/slideMaster1.xml"),
        CT.PML_SLIDE_MASTER,
        Package(None),
        parse_xml(
            b'<p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree/></p:cSld></p:sldMaster>'
        ),
    )
    expected_layout = object()
    part.related_part = lambda rid: SlideLayoutPartProxy(expected_layout)  # type: ignore[method-assign]

    assert part.related_slide_layout("rId5") is expected_layout
