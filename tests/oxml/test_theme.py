from __future__ import annotations

from syrupy.assertion import SnapshotAssertion

from pptx.oxml.theme import CT_OfficeStyleSheet


def test_ct_office_style_sheet_new_default(snapshot: SnapshotAssertion) -> None:
    theme = CT_OfficeStyleSheet.new_default()

    assert str(theme.xml) == snapshot
