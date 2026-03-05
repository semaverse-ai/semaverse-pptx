from __future__ import annotations

import pytest
from syrupy.assertion import SnapshotAssertion

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
def test_connector_new_cxnSp(
    flip_h: bool, flip_v: bool, snapshot: SnapshotAssertion
) -> None:
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

    assert str(cxn_sp.xml) == snapshot
