from __future__ import annotations

import pytest

from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.oxml import parse_xml
from pptx.package import Package
from pptx.parts.presentation import PresentationPart
from pptx.parts.slide import SlideLayoutPart, SlidePart
from pptx.slide import SlideLayout
from tests.stubs import (
    CorePropertiesPackageStub,
    NotesMasterPartProxy,
    SaveCallPackageStub,
    SlideMasterPartProxy,
    SlidePartProxy,
)

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


def test_presentation_part_core_properties_delegates_to_package() -> None:
    expected_core_props = object()

    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        CorePropertiesPackageStub(expected_core_props),
        parse_xml(_presentation_xml()),
    )

    # Act / Assert
    assert part.core_properties is expected_core_props


def test_presentation_part_get_slide_returns_slide_or_none() -> None:
    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        None,
        parse_xml(
            b"""
            <p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
              <p:sldIdLst>
                <p:sldId id="256" r:id="rId1"/>
              </p:sldIdLst>
            </p:presentation>
            """
        ),
    )
    expected_slide = object()
    part.related_part = lambda rid: SlidePartProxy(expected_slide)  # type: ignore[method-assign]

    # Act / Assert
    assert part.get_slide(256) is expected_slide
    assert part.get_slide(999) is None


def test_presentation_part_notes_master_part_existing_relation_path() -> None:
    expected = object()
    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        None,
        parse_xml(_presentation_xml()),
    )
    part.part_related_by = lambda reltype: expected  # type: ignore[method-assign]

    # Act / Assert
    assert part.notes_master_part is expected


def test_presentation_part_notes_master_part_create_default_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created = object()
    relate_calls: list[tuple[object, str]] = []
    package = Package(None)
    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        package,
        parse_xml(_presentation_xml()),
    )

    def _part_related_by(_reltype: str):
        raise KeyError

    def _relate_to(target: object, reltype: str) -> None:
        relate_calls.append((target, reltype))

    part.part_related_by = _part_related_by  # type: ignore[method-assign]
    part.relate_to = _relate_to  # type: ignore[method-assign]
    monkeypatch.setattr(
        "pptx.parts.presentation.NotesMasterPart.create_default", lambda pkg: created
    )

    notes_master_part = part.notes_master_part

    assert notes_master_part is created
    assert relate_calls == [(created, RT.NOTES_MASTER)]


def test_presentation_part_notes_master_related_slide_and_related_master() -> None:
    notes_master = object()
    slide = object()
    slide_master = object()
    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        None,
        parse_xml(_presentation_xml()),
    )

    def _related_part(rid: str):
        mapping = {
            "notes": NotesMasterPartProxy(notes_master),
            "slide": SlidePartProxy(slide),
            "master": SlideMasterPartProxy(slide_master),
        }
        return mapping[rid]

    part.part_related_by = lambda reltype: _related_part("notes")  # type: ignore[method-assign]
    part.related_part = _related_part  # type: ignore[method-assign]

    # Act / Assert
    assert part.notes_master is notes_master
    assert part.related_slide("slide") is slide
    assert part.related_slide_master("master") is slide_master


def test_presentation_part_save_delegates_to_package() -> None:
    package = SaveCallPackageStub()

    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        package,
        parse_xml(_presentation_xml()),
    )

    part.save("out.pptx")

    assert package.saved_paths == ["out.pptx"]


def test_presentation_part_slide_id_returns_match_and_raises_when_missing() -> None:
    target_part = object()
    non_target = object()
    part = PresentationPart(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        None,
        parse_xml(
            b"""
            <p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
              <p:sldIdLst>
                <p:sldId id="256" r:id="rId1"/>
                <p:sldId id="257" r:id="rId2"/>
              </p:sldIdLst>
            </p:presentation>
            """
        ),
    )
    part.related_part = (  # type: ignore[method-assign]
        lambda rid: target_part if rid == "rId2" else non_target
    )

    # Act / Assert
    assert part.slide_id(target_part) == 257

    with pytest.raises(ValueError, match="matching slide_part not found"):
        part.slide_id(object())
