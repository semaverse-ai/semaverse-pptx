from __future__ import annotations

from collections.abc import Iterable
from xml.sax.saxutils import escape

from pptx.oxml import parse_xml

_PML = "http://schemas.openxmlformats.org/presentationml/2006/main"
_DML = "http://schemas.openxmlformats.org/drawingml/2006/main"


def _xfrm_xml(x: int, y: int, cx: int, cy: int, rot: int | None) -> str:
    rot_attr = f' rot="{rot}"' if rot is not None else ""
    return (
        f"<a:xfrm{rot_attr}>"
        f'<a:off x="{x}" y="{y}"/>'
        f'<a:ext cx="{cx}" cy="{cy}"/>'
        "</a:xfrm>"
    )


def make_sp(
    *,
    shape_id: int,
    name: str,
    x: int | None = None,
    y: int | None = None,
    cx: int | None = None,
    cy: int | None = None,
    rot: int | None = None,
    prst: str | None = None,
    placeholder_attrs: str | None = None,
    with_text_body: bool = False,
    text: str | None = None,
) -> object:
    return parse_xml(
        _sp_xml(
            shape_id=shape_id,
            name=name,
            x=x,
            y=y,
            cx=cx,
            cy=cy,
            rot=rot,
            prst=prst,
            placeholder_attrs=placeholder_attrs,
            with_text_body=with_text_body,
            text=text,
            include_namespaces=True,
        )
    )


def make_sp_snippet(
    *,
    shape_id: int,
    name: str,
    x: int | None = None,
    y: int | None = None,
    cx: int | None = None,
    cy: int | None = None,
    rot: int | None = None,
    prst: str | None = None,
    placeholder_attrs: str | None = None,
    with_text_body: bool = False,
    text: str | None = None,
) -> str:
    return _sp_xml(
        shape_id=shape_id,
        name=name,
        x=x,
        y=y,
        cx=cx,
        cy=cy,
        rot=rot,
        prst=prst,
        placeholder_attrs=placeholder_attrs,
        with_text_body=with_text_body,
        text=text,
        include_namespaces=False,
    ).decode("utf-8")


def make_group(
    *,
    shape_id: int,
    name: str,
    with_xfrm: bool = False,
    children: Iterable[str] = (),
) -> object:
    grp_sp_pr = (
        "<p:grpSpPr>"
        "<a:xfrm>"
        '<a:off x="0" y="0"/>'
        '<a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/>'
        '<a:chExt cx="0" cy="0"/>'
        "</a:xfrm>"
        "</p:grpSpPr>"
        if with_xfrm
        else "<p:grpSpPr/>"
    )
    xml = (
        f'<p:grpSp xmlns:p="{_PML}" xmlns:a="{_DML}">'
        "<p:nvGrpSpPr>"
        f'<p:cNvPr id="{shape_id}" name="{escape(name)}"/>'
        "<p:cNvGrpSpPr/>"
        "<p:nvPr/>"
        "</p:nvGrpSpPr>"
        f"{grp_sp_pr}"
        f"{''.join(children)}"
        "</p:grpSp>"
    )
    return parse_xml(xml.encode("utf-8"))


def _sp_xml(
    *,
    shape_id: int,
    name: str,
    x: int | None,
    y: int | None,
    cx: int | None,
    cy: int | None,
    rot: int | None,
    prst: str | None,
    placeholder_attrs: str | None,
    with_text_body: bool,
    text: str | None,
    include_namespaces: bool,
) -> bytes:
    if any(v is not None for v in (x, y, cx, cy)) and any(v is None for v in (x, y, cx, cy)):
        raise ValueError("x, y, cx, cy must be provided together")

    sp_pr_children: list[str] = []
    if x is not None and y is not None and cx is not None and cy is not None:
        sp_pr_children.append(_xfrm_xml(x, y, cx, cy, rot))
    if prst is not None:
        sp_pr_children.append(f'<a:prstGeom prst="{prst}"/>')

    sp_pr = "<p:spPr/>" if not sp_pr_children else f"<p:spPr>{''.join(sp_pr_children)}</p:spPr>"
    nv_pr = (
        f"<p:nvPr><p:ph {placeholder_attrs}/></p:nvPr>"
        if placeholder_attrs is not None
        else "<p:nvPr/>"
    )

    if with_text_body and text is not None:
        tx_body = (
            "<p:txBody><a:bodyPr/><a:lstStyle/>"
            f"<a:p><a:r><a:t>{escape(text)}</a:t></a:r></a:p>"
            "</p:txBody>"
        )
    elif with_text_body:
        tx_body = "<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>"
    else:
        tx_body = ""

    ns_decl = f' xmlns:p="{_PML}" xmlns:a="{_DML}"' if include_namespaces else ""

    xml = (
        f"<p:sp{ns_decl}>"
        "<p:nvSpPr>"
        f'<p:cNvPr id="{shape_id}" name="{escape(name)}"/>'
        "<p:cNvSpPr/>"
        f"{nv_pr}"
        "</p:nvSpPr>"
        f"{sp_pr}"
        f"{tx_body}"
        "</p:sp>"
    )
    return xml.encode("utf-8")
