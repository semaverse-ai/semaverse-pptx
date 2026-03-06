from __future__ import annotations

import pytest

from pptx.oxml.shapes.connector import CT_Connector


@pytest.mark.parametrize(
    ("flip_h", "flip_v"),
    [
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_connector_new_cxnSp(flip_h: bool, flip_v: bool) -> None:
    cxn_sp = CT_Connector.new_cxnSp(
        id_=42,
        name="Connector 41",
        prst="line",
        x=1,
        y=2,
        cx=3,
        cy=4,
        flipH=flip_h,
        flipV=flip_v,
    )

    assert cxn_sp.nvCxnSpPr.cNvPr.id == 42
    assert cxn_sp.nvCxnSpPr.cNvPr.name == "Connector 41"
    assert cxn_sp.spPr.xfrm.flipH is flip_h
    assert cxn_sp.spPr.xfrm.flipV is flip_v
