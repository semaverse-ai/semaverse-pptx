from __future__ import annotations

import io
from pathlib import Path

import pytest

from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.package import OpcPackage, Part, PartFactory, _ContentTypeMap, _Relationships
from pptx.opc.packuri import PackURI
from pptx.parts.presentation import PresentationPart


@pytest.fixture
def package() -> OpcPackage:
    return OpcPackage(None)


def test_relatable_mixin_relate_to_part(package: OpcPackage) -> None:
    part = Part(PackURI("/ppt/slides/slide1.xml"), "app/vnd.slide", package)

    rId = package.relate_to(part, RT.SLIDE)

    assert rId == "rId1"
    assert package.part_related_by(RT.SLIDE) is part
    assert package.related_part(rId) is part
    assert package.target_ref(rId) == "ppt/slides/slide1.xml"


def test_relatable_mixin_relate_to_external(package: OpcPackage) -> None:
    rId = package.relate_to("http://example.com", RT.HYPERLINK, is_external=True)

    assert rId == "rId1"
    assert package.target_ref(rId) == "http://example.com"


def test_package_drop_rel(package: OpcPackage) -> None:
    part = Part(PackURI("/ppt/slides/slide1.xml"), "app/vnd.slide", package)
    rId = package.relate_to(part, RT.SLIDE)

    assert rId in package._rels

    package.drop_rel(rId)

    assert rId not in package._rels


def test_package_next_partname(package: OpcPackage) -> None:
    part1 = Part(PackURI("/ppt/slides/slide1.xml"), "app/vnd.slide", package)
    part2 = Part(PackURI("/ppt/slides/slide2.xml"), "app/vnd.slide", package)
    package.relate_to(part1, RT.SLIDE)
    package.relate_to(part2, RT.SLIDE)

    next_uri = package.next_partname("/ppt/slides/slide%d.xml")

    assert next_uri == "/ppt/slides/slide3.xml"


def test_part_blob_from_file_path(tmp_path: Path, package: OpcPackage) -> None:
    data = b"abc123"
    file_path = tmp_path / "payload.bin"
    file_path.write_bytes(data)
    part = Part(PackURI("/foo.bin"), "application/octet-stream", package)

    blob = part._blob_from_file(str(file_path))

    assert blob == data


def test_part_blob_from_file_like(package: OpcPackage) -> None:
    stream = io.BytesIO(b"bytes-from-stream")
    part = Part(PackURI("/foo.bin"), "application/octet-stream", package)

    blob = part._blob_from_file(stream)

    assert blob == b"bytes-from-stream"


def test_part_factory_returns_part(package: OpcPackage) -> None:
    part = PartFactory(PackURI("/foo.xml"), "app/vnd.foo", package, b"<foo/>")

    assert type(part) is Part


def test_part_factory_returns_presentation_part(
    package: OpcPackage, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(PartFactory.part_type_for, CT.PML_PRESENTATION_MAIN, PresentationPart)

    part = PartFactory(
        PackURI("/ppt/presentation.xml"),
        CT.PML_PRESENTATION_MAIN,
        package,
        b'<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>',
    )

    assert type(part) is PresentationPart


def test_content_type_map() -> None:
    ct_map = _ContentTypeMap(
        overrides={"/ppt/presentation.xml": "app/vnd.pres"},
        defaults={"xml": "application/xml"},
    )

    assert ct_map[PackURI("/ppt/presentation.xml")] == "app/vnd.pres"
    assert ct_map[PackURI("/foo.xml")] == "application/xml"

    with pytest.raises(KeyError):
        _ = ct_map[PackURI("/foo.bar")]

    with pytest.raises(TypeError):
        _ = ct_map["/foo.xml"]


def test_content_type_map_from_xml() -> None:
    xml = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        b'<Default Extension="xml" ContentType="application/xml"/>'
        b'<Override PartName="/ppt/presentation.xml" ContentType="app/vnd.pres"/>'
        b"</Types>"
    )

    ct_map = _ContentTypeMap.from_xml(xml)

    assert ct_map[PackURI("/PPT/PRESENTATION.XML")] == "app/vnd.pres"
    assert ct_map[PackURI("/foo.xml")] == "application/xml"


def test_relationships_get_or_add() -> None:
    rels = _Relationships("/")
    package = OpcPackage(None)
    part = Part(PackURI("/foo.xml"), "app/vnd.foo", package)

    rId = rels.get_or_add(RT.SLIDE, part)
    rId2 = rels.get_or_add(RT.SLIDE, part)

    assert rId == "rId1"
    assert rId2 == "rId1"
    assert len(rels) == 1


def test_relationships_get_or_add_ext_rel() -> None:
    rels = _Relationships("/")

    rId = rels.get_or_add_ext_rel(RT.HYPERLINK, "http://foo.com")
    rId2 = rels.get_or_add_ext_rel(RT.HYPERLINK, "http://foo.com")

    assert rId == "rId1"
    assert rId2 == "rId1"
    assert len(rels) == 1


def test_relationships_pop() -> None:
    rels = _Relationships("/")
    package = OpcPackage(None)
    part = Part(PackURI("/foo.xml"), "app/vnd.foo", package)
    rId = rels.get_or_add(RT.SLIDE, part)

    popped = rels.pop(rId)

    assert popped.rId == "rId1"
    assert len(rels) == 0


def test_relationships_part_with_reltype_raises_on_missing() -> None:
    rels = _Relationships("/")

    with pytest.raises(KeyError):
        rels.part_with_reltype(RT.SLIDE)
