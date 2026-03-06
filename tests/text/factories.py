from __future__ import annotations

from pptx.oxml import parse_xml

PML_NS = b"http://schemas.openxmlformats.org/presentationml/2006/main"
DML_NS = b"http://schemas.openxmlformats.org/drawingml/2006/main"
REL_NS = b"http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def tx_body(xml_body: bytes = b"") -> object:
    return parse_xml(
        b'<p:txBody xmlns:p="'
        + PML_NS
        + b'" xmlns:a="'
        + DML_NS
        + b'" xmlns:r="'
        + REL_NS
        + b'">'
        + xml_body
        + b"</p:txBody>"
    )


def paragraph(xml_body: bytes = b"") -> object:
    return parse_xml(b'<a:p xmlns:a="' + DML_NS + b'">' + xml_body + b"</a:p>")


def run(xml_body: bytes = b"") -> object:
    return parse_xml(
        b'<a:r xmlns:a="' + DML_NS + b'" xmlns:r="' + REL_NS + b'">' + xml_body + b"</a:r>"
    )


def table(xml_body: bytes = b"") -> object:
    return parse_xml(b'<a:tbl xmlns:a="' + DML_NS + b'">' + xml_body + b"</a:tbl>")
