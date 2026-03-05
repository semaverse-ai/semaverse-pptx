from __future__ import annotations

import pytest
from lxml import etree

from pptx.oxml import oxml_parser, parse_xml, register_element_cls
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import BaseOxmlElement


class CT_Ticket4Custom(BaseOxmlElement):
    pass


def test_oxml_parser_strips_whitespace_between_elements() -> None:
    xml_text = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<a:foo xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">\n'
        "  <a:bar>foobar</a:bar>\n"
        "</a:foo>\n"
    )

    element = etree.fromstring(xml_text.encode("utf-8"), oxml_parser)
    xml_bytes = etree.tostring(element)

    assert xml_bytes == (
        b'<a:foo xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        b"<a:bar>foobar</a:bar></a:foo>"
    )


def test_parse_xml_prefers_to_parse_bytes() -> None:
    xml_bytes = b"<foo><bar>foobar</bar></foo>"

    element = parse_xml(xml_bytes)

    assert element.tag == "foo"


def test_parse_xml_accepts_unicode_without_encoding_declaration() -> None:
    xml_text = '<?xml version="1.0" standalone="yes"?>\n<foo><bar>foobaz</bar></foo>'

    element = parse_xml(xml_text)

    assert element.tag == "foo"


def test_parse_xml_raises_on_unicode_with_encoding_declaration() -> None:
    xml_text = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<foo><bar>x</bar></foo>'

    with pytest.raises(ValueError):
        parse_xml(xml_text)


def test_register_element_cls_registers_custom_type_for_tag() -> None:
    register_element_cls("a:ticket4Custom", CT_Ticket4Custom)

    element = etree.fromstring(
        (
            '<a:ticket4Custom xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            "<a:bar>foobar</a:bar>"
            "</a:ticket4Custom>"
        ).encode("utf-8"),
        oxml_parser,
    )

    assert isinstance(element, CT_Ticket4Custom)
    assert type(element.find(qn("a:bar"))) is etree._Element
