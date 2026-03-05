from __future__ import annotations

from typing import cast

from syrupy.assertion import SnapshotAssertion

from pptx.opc.constants import RELATIONSHIP_TARGET_MODE as RTM
from pptx.opc.oxml import (
    CT_Default,
    CT_Override,
    CT_Relationship,
    CT_Relationships,
    CT_Types,
    serialize_part_xml,
)
from pptx.opc.packuri import PackURI
from pptx.oxml import parse_xml


def test_ct_default_properties() -> None:
    default = cast(
        CT_Default,
        parse_xml(
            '<Default xmlns="http://schemas.openxmlformats.org/package/2006/content-types" '
            'Extension="xml" ContentType="application/xml"/>'
        ),
    )

    assert default.extension == "xml"
    assert default.contentType == "application/xml"


def test_ct_override_properties() -> None:
    override = cast(
        CT_Override,
        parse_xml(
            '<Override xmlns="http://schemas.openxmlformats.org/package/2006/content-types" '
            'PartName="/part/name.xml" ContentType="text/plain"/>'
        ),
    )

    assert override.partName == "/part/name.xml"
    assert override.contentType == "text/plain"


def test_ct_relationship_properties() -> None:
    rel = cast(
        CT_Relationship,
        parse_xml(
            '<Relationship xmlns="http://schemas.openxmlformats.org/package/2006/relationships" '
            'Id="rId9" Type="ReLtYpE" Target="docProps/core.xml"/>'
        ),
    )

    assert rel.rId == "rId9"
    assert rel.reltype == "ReLtYpE"
    assert rel.target_ref == "docProps/core.xml"
    assert rel.targetMode == RTM.INTERNAL


def test_ct_relationship_new_internal(snapshot: SnapshotAssertion) -> None:
    rel = CT_Relationship.new("rId9", "ReLtYpE", "foo/bar.xml")

    assert rel.rId == "rId9"
    assert rel.reltype == "ReLtYpE"
    assert rel.target_ref == "foo/bar.xml"
    assert rel.targetMode == RTM.INTERNAL
    assert snapshot == rel.xml


def test_ct_relationship_new_external(snapshot: SnapshotAssertion) -> None:
    rel = CT_Relationship.new("rId9", "ReLtYpE", "http://some/link", RTM.EXTERNAL)

    assert rel.rId == "rId9"
    assert rel.reltype == "ReLtYpE"
    assert rel.target_ref == "http://some/link"
    assert rel.targetMode == RTM.EXTERNAL
    assert snapshot == rel.xml


def test_ct_relationships_new(snapshot: SnapshotAssertion) -> None:
    rels = CT_Relationships.new()

    assert snapshot == rels.xml


def test_ct_relationships_add_rel(snapshot: SnapshotAssertion) -> None:
    rels = CT_Relationships.new()
    rels.add_rel("rId1", "http://reltype1", "docProps/core.xml")
    rels.add_rel("rId2", "http://linktype", "http://some/link", True)
    rels.add_rel("rId3", "http://reltype2", "../slides/slide1.xml")

    assert snapshot == rels.xml


def test_ct_relationships_xml_file_bytes(snapshot: SnapshotAssertion) -> None:
    rels = CT_Relationships.new()

    assert snapshot == rels.xml_file_bytes.decode("utf-8")


def test_ct_types_new(snapshot: SnapshotAssertion) -> None:
    types = CT_Types.new()

    assert snapshot == types.xml


def test_ct_types_add_default_override(snapshot: SnapshotAssertion) -> None:
    types = CT_Types.new()
    types.add_default("xml", "application/xml")
    types.add_default("jpeg", "image/jpeg")
    types.add_override(PackURI("/docProps/core.xml"), "app/vnd.type1")
    types.add_override(PackURI("/ppt/presentation.xml"), "app/vnd.type2")
    types.add_override(PackURI("/docProps/thumbnail.jpeg"), "image/jpeg")

    assert snapshot == types.xml


def test_serialize_part_xml(snapshot: SnapshotAssertion) -> None:
    part_elm = parse_xml('<f:foo xmlns:f="http://foo"><f:bar>foobar</f:bar></f:foo>')
    xml_bytes = serialize_part_xml(part_elm)

    assert snapshot == xml_bytes.decode("utf-8")
