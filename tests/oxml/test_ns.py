from __future__ import annotations

from pptx.oxml.ns import NamespacePrefixedTag, namespaces, nsdecls, nsuri, qn


def test_namespace_prefixed_tag_behavior() -> None:
    namespace_uri = "http://schemas.openxmlformats.org/drawingml/2006/main"
    nsptag = NamespacePrefixedTag("a:foobar")

    assert f"- {nsptag} -" == "- a:foobar -"
    assert nsptag.clark_name == f"{{{namespace_uri}}}foobar"
    assert nsptag.local_part == "foobar"
    assert nsptag.nsmap == {"a": namespace_uri}
    assert nsptag.nspfx == "a"
    assert nsptag.nsuri == namespace_uri


def test_namespaces() -> None:
    assert namespaces("a", "p") == {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    }


def test_nsdecls() -> None:
    assert nsdecls("a", "p") == (
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    )


def test_nsuri() -> None:
    assert nsuri("a") == "http://schemas.openxmlformats.org/drawingml/2006/main"


def test_qn() -> None:
    assert qn("a:foobar") == "{http://schemas.openxmlformats.org/drawingml/2006/main}foobar"
