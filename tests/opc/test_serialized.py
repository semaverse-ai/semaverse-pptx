from __future__ import annotations

import io
import zipfile

import pytest

from pptx.exc import PackageNotFoundError
from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.package import Part, _Relationships
from pptx.opc.packuri import PackURI
from pptx.opc.serialized import (
    PackageReader,
    PackageWriter,
    _ContentTypesItem,
    _PhysPkgReader,
    _ZipPkgReader,
    _ZipPkgWriter,
)
from tests.xml_utils import xml_string_eq_ignores_attribute_order


def test_phys_pkg_reader_factory_raises_on_not_found() -> None:
    with pytest.raises(PackageNotFoundError):
        _PhysPkgReader.factory("/path/does/not/exist/non_existent_file.pptx")


def test_zip_pkg_reader_contains_and_getitem() -> None:
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as z:
        z.writestr("ppt/presentation.xml", b"content")

    zip_bytes.seek(0)
    reader = _ZipPkgReader(zip_bytes)

    assert PackURI("/ppt/presentation.xml") in reader
    assert PackURI("/ppt/foo.xml") not in reader
    assert reader[PackURI("/ppt/presentation.xml")] == b"content"

    with pytest.raises(KeyError):
        _ = reader[PackURI("/ppt/foo.xml")]


def test_zip_pkg_writer_write() -> None:
    zip_bytes = io.BytesIO()

    with _ZipPkgWriter(zip_bytes) as writer:
        writer.write(PackURI("/ppt/foo.xml"), b"content")

    zip_bytes.seek(0)
    with zipfile.ZipFile(zip_bytes, "r") as z:
        assert z.read("ppt/foo.xml") == b"content"


def test_package_reader_rels_xml_for() -> None:
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as z:
        z.writestr("ppt/slides/slide1.xml", b"<p:sld/>")
        z.writestr(
            "ppt/slides/_rels/slide1.xml.rels",
            b"<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'/>",
        )

    zip_bytes.seek(0)
    reader = PackageReader(zip_bytes)

    rels_xml = reader.rels_xml_for(PackURI("/ppt/slides/slide1.xml"))

    assert rels_xml is not None
    assert b"Relationships" in rels_xml


def test_package_writer_write() -> None:
    package_rels = _Relationships("/")
    package = type("Pkg", (), {})()
    part = Part(PackURI("/ppt/slides/slide1.xml"), CT.PML_SLIDE, package, b"<p:sld/>")

    package_rels.get_or_add(RT.SLIDE, part)

    zip_bytes = io.BytesIO()

    PackageWriter.write(zip_bytes, package_rels, [part])

    zip_bytes.seek(0)
    with zipfile.ZipFile(zip_bytes, "r") as z:
        names = set(z.namelist())

    assert "[Content_Types].xml" in names
    assert "_rels/.rels" in names
    assert "ppt/slides/slide1.xml" in names


def test_content_types_item_xml_for() -> None:
    parts = [
        Part(PackURI("/media/image1.png"), CT.PNG, None),
        Part(PackURI("/ppt/slides/slide1.xml"), CT.PML_SLIDE, None),
        Part(PackURI("/docProps/core.xml"), CT.OPC_CORE_PROPERTIES, None),
    ]

    xml = _ContentTypesItem.xml_for(parts).xml

    expected_xml = """
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
      <Default Extension="png" ContentType="image/png"/>
      <Default
        Extension="rels"
        ContentType="application/vnd.openxmlformats-package.relationships+xml"
      />
      <Default Extension="xml" ContentType="application/xml"/>
      <Override
        PartName="/docProps/core.xml"
        ContentType="application/vnd.openxmlformats-package.core-properties+xml"
      />
      <Override
        PartName="/ppt/slides/slide1.xml"
        ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
      />
    </Types>
    """
    assert xml_string_eq_ignores_attribute_order(xml, expected_xml)
