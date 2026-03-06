from __future__ import annotations

from typing import TYPE_CHECKING
from xml.sax.saxutils import quoteattr

import pytest

from pptx.oxml import parse_xml

if TYPE_CHECKING:
    from pptx.oxml.action import CT_Hyperlink


def _hlink(action: str | None = None, r_id: str | None = None) -> CT_Hyperlink:
    attrs = []
    if action is not None:
        attrs.append(f"action={quoteattr(action)}")
    if r_id is not None:
        attrs.append(f"r:id={quoteattr(r_id)}")

    attr_xml = (" " + " ".join(attrs)) if attrs else ""
    xml = (
        '<a:hlinkClick xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        f"{attr_xml}/>"
    )
    return parse_xml(xml.encode("utf-8"))


@pytest.mark.parametrize(
    ("action", "expected_fields"),
    [
        (None, {}),
        ("ppaction://macro", {}),
        ("ppaction://customshow?id=0", {"id": "0"}),
        ("ppaction://customshow?id=0&return=true", {"id": "0", "return": "true"}),
    ],
)
def test_ct_hyperlink_action_fields(action: str | None, expected_fields: dict[str, str]) -> None:
    hlink = _hlink(action=action)

    fields = hlink.action_fields

    assert fields == expected_fields


@pytest.mark.parametrize(
    ("action", "expected_verb"),
    [
        (None, None),
        ("ppaction://macro", "macro"),
        ("ppaction://customshow?id=0&return=true", "customshow"),
    ],
)
def test_ct_hyperlink_action_verb(action: str | None, expected_verb: str | None) -> None:
    hlink = _hlink(action=action)

    verb = hlink.action_verb

    assert verb == expected_verb


def test_ct_hyperlink_optional_attributes_round_trip() -> None:
    hlink = _hlink()

    hlink.rId = "rId42"
    hlink.action = "ppaction://program"
    hlink.action = None

    assert hlink.rId == "rId42"
    assert hlink.action is None
