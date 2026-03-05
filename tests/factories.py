from __future__ import annotations

PML_NS = b"http://schemas.openxmlformats.org/presentationml/2006/main"
DML_NS = b"http://schemas.openxmlformats.org/drawingml/2006/main"
REL_NS = b"http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def sp_tree_body(shape_children: bytes = b"") -> bytes:
    return b"".join(
        [
            b"""
            <p:spTree>
              <p:nvGrpSpPr>
                <p:cNvPr id="1" name=""/>
                <p:cNvGrpSpPr/>
                <p:nvPr/>
              </p:nvGrpSpPr>
              <p:grpSpPr>
                <a:xfrm>
                  <a:off x="0" y="0"/>
                  <a:ext cx="0" cy="0"/>
                  <a:chOff x="0" y="0"/>
                  <a:chExt cx="0" cy="0"/>
                </a:xfrm>
              </p:grpSpPr>
            """,
            shape_children,
            b"""
            </p:spTree>
            """,
        ]
    )


def slide_xml(sp_children: bytes = b"", *, with_bg: bool = False) -> bytes:
    bg = b"<p:bg/>" if with_bg else b""
    return b"".join(
        [
            b'<p:sld xmlns:p="',
            PML_NS,
            b'" xmlns:a="',
            DML_NS,
            b'" xmlns:r="',
            REL_NS,
            b'"><p:cSld>',
            bg,
            sp_tree_body(sp_children),
            b"</p:cSld></p:sld>",
        ]
    )


def notes_xml(sp_children: bytes = b"") -> bytes:
    return b"".join(
        [
            b'<p:notes xmlns:p="',
            PML_NS,
            b'" xmlns:a="',
            DML_NS,
            b'"><p:cSld>',
            sp_tree_body(sp_children),
            b"</p:cSld></p:notes>",
        ]
    )


def notes_master_xml(sp_children: bytes = b"") -> bytes:
    return b"".join(
        [
            b'<p:notesMaster xmlns:p="',
            PML_NS,
            b'" xmlns:a="',
            DML_NS,
            b'"><p:cSld>',
            sp_tree_body(sp_children),
            b"</p:cSld></p:notesMaster>",
        ]
    )


def slide_layout_xml(sp_children: bytes = b"") -> bytes:
    return b"".join(
        [
            b'<p:sldLayout xmlns:p="',
            PML_NS,
            b'" xmlns:a="',
            DML_NS,
            b'" xmlns:r="',
            REL_NS,
            b'"><p:cSld>',
            sp_tree_body(sp_children),
            b"</p:cSld></p:sldLayout>",
        ]
    )


def slide_master_xml(sp_children: bytes = b"") -> bytes:
    return b"".join(
        [
            b'<p:sldMaster xmlns:p="',
            PML_NS,
            b'" xmlns:a="',
            DML_NS,
            b'"><p:cSld>',
            sp_tree_body(sp_children),
            b"</p:cSld><p:sldLayoutIdLst/></p:sldMaster>",
        ]
    )


def presentation_xml(inner: bytes = b"") -> bytes:
    return b"".join(
        [
            b'<p:presentation xmlns:p="',
            PML_NS,
            b'" xmlns:r="',
            REL_NS,
            b'">',
            inner,
            b"</p:presentation>",
        ]
    )
