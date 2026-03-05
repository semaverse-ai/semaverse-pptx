from __future__ import annotations

from lxml import etree


def serialize_xml(element: object) -> str:
    """Return stable pretty-printed XML for snapshot assertions."""
    return etree.tostring(element, pretty_print=True, encoding="unicode")
