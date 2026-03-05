from __future__ import annotations

from lxml import etree
from lxml.doctestcompare import PARSE_XML, LXMLOutputChecker

_XML_OUTPUT_CHECKER = LXMLOutputChecker()


def _as_text(xml: str | bytes) -> str:
    return xml.decode("utf-8") if isinstance(xml, bytes) else xml


def serialize_xml(element: object) -> str:
    """Return stable pretty-printed XML for snapshot assertions."""
    return etree.tostring(element, pretty_print=True, encoding="unicode")


def canonical_xml(xml: str | bytes) -> str:
    """Return canonical XML (C14N) for stable semantic comparisons."""
    xml_bytes = xml.encode("utf-8") if isinstance(xml, str) else xml
    parser = etree.XMLParser(remove_blank_text=True)
    element = etree.fromstring(xml_bytes, parser=parser)
    return etree.tostring(element, method="c14n", with_comments=False).decode("utf-8")


def xml_string_eq_ignores_attribute_order(xml1: str | bytes, xml2: str | bytes) -> bool:
    """Return True when XML payloads are semantically equal."""
    return _XML_OUTPUT_CHECKER.check_output(_as_text(xml1), _as_text(xml2), PARSE_XML)
