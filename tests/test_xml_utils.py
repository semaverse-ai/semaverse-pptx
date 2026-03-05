from __future__ import annotations

from tests.xml_utils import xml_string_eq_ignores_attribute_order


def test_xml_equivalence_ignores_attribute_order() -> None:
    left = '<a:foo xmlns:a="urn:test" x="1" y="2"/>'
    right = '<a:foo y="2" xmlns:a="urn:test" x="1"/>'

    assert xml_string_eq_ignores_attribute_order(left, right)


def test_xml_equivalence_ignores_indentation_and_linebreaks() -> None:
    left = '<a:foo xmlns:a="urn:test"><a:bar id="1"/></a:foo>'
    right = """
    <a:foo xmlns:a="urn:test">
      <a:bar id="1"/>
    </a:foo>
    """

    assert xml_string_eq_ignores_attribute_order(left, right)


def test_xml_equivalence_detects_structural_difference() -> None:
    left = '<a:foo xmlns:a="urn:test"><a:bar/></a:foo>'
    right = '<a:foo xmlns:a="urn:test"><a:baz/></a:foo>'

    assert not xml_string_eq_ignores_attribute_order(left, right)


def test_xml_equivalence_accepts_mixed_text_and_bytes_inputs() -> None:
    left = '<a:foo xmlns:a="urn:test"><a:bar id="1"/></a:foo>'
    right = b'<a:foo xmlns:a="urn:test"><a:bar id="1"/></a:foo>'

    assert xml_string_eq_ignores_attribute_order(left, right)
