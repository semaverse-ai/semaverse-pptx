from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.packuri import PackURI
from pptx.package import Package
from pptx.parts.coreprops import CorePropertiesPart


@pytest.fixture
def core_properties_part(test_files_dir: Path) -> CorePropertiesPart:
    xml = (test_files_dir / "coreprops-modern.xml").read_bytes()
    package = Package(None)

    return CorePropertiesPart.load(
        PackURI("/docProps/core.xml"),
        CT.OPC_CORE_PROPERTIES,
        package,
        xml,
    )


@pytest.mark.parametrize(
    ("prop_name", "expected_value"),
    [
        ("author", "semaverse-pptx"),
        ("category", ""),
        ("comments", ""),
        ("content_status", "DRAFT"),
        ("identifier", "GXS 10.2.1ab"),
        ("keywords", "foo bar baz"),
        ("language", "US-EN"),
        ("last_modified_by", "semaverse-ai"),
        ("subject", "Spam"),
        ("title", "Presentation"),
        ("version", "1.2.88"),
    ],
)
def test_core_props_string_getters(
    core_properties_part: CorePropertiesPart, prop_name: str, expected_value: str
) -> None:
    assert getattr(core_properties_part, prop_name) == expected_value


@pytest.mark.parametrize(
    ("prop_name", "value"),
    [
        ("author", "semaverse-ai"),
        ("category", "silly stories"),
        ("comments", "Bar foo to you"),
        ("content_status", "FINAL"),
        ("identifier", "GT 5.2.xab"),
        ("keywords", "dog cat moo"),
        ("language", "GB-EN"),
        ("last_modified_by", "Billy Bob"),
        ("subject", "Eggs"),
        ("title", "Dissertation"),
        ("version", "81.2.8"),
    ],
)
def test_core_props_string_setters(
    core_properties_part: CorePropertiesPart,
    prop_name: str,
    value: str,
) -> None:
    setattr(core_properties_part, prop_name, value)

    assert getattr(core_properties_part, prop_name) == value


@pytest.mark.parametrize(
    ("prop_name", "expected_value"),
    [
        ("created", dt.datetime(2012, 11, 17, 16, 37, 40)),
        ("last_printed", dt.datetime(2014, 6, 4, 4, 28)),
        ("modified", None),
    ],
)
def test_core_props_date_getters(
    core_properties_part: CorePropertiesPart,
    prop_name: str,
    expected_value: dt.datetime | None,
) -> None:
    assert getattr(core_properties_part, prop_name) == expected_value


@pytest.mark.parametrize(
    ("prop_name", "value"),
    [
        ("created", dt.datetime(2001, 2, 3, 4, 5)),
        ("last_printed", dt.datetime(2014, 6, 4, 4)),
        ("modified", dt.datetime(2005, 4, 3, 2, 1)),
    ],
)
def test_core_props_date_setters(
    core_properties_part: CorePropertiesPart,
    prop_name: str,
    value: dt.datetime,
) -> None:
    setattr(core_properties_part, prop_name, value)

    assert getattr(core_properties_part, prop_name) == value


def test_core_props_revision_getter(core_properties_part: CorePropertiesPart) -> None:
    assert core_properties_part.revision == 4


def test_core_props_revision_setter(core_properties_part: CorePropertiesPart) -> None:
    core_properties_part.revision = 42

    assert core_properties_part.revision == 42


def test_core_props_default() -> None:
    pkg = Package(None)

    core_props = CorePropertiesPart.default(pkg)

    assert isinstance(core_props, CorePropertiesPart)
    assert core_props.content_type == CT.OPC_CORE_PROPERTIES
    assert core_props.partname == "/docProps/core.xml"
    assert core_props.title == "PowerPoint Presentation"
    assert core_props.last_modified_by == "semaverse-pptx"
    assert core_props.revision == 1
    assert core_props.modified is not None
