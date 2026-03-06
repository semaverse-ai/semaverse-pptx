from __future__ import annotations

from pptx.oxml.ns import qn
from pptx.oxml.theme import CT_OfficeStyleSheet


def test_ct_office_style_sheet_new_default() -> None:
    theme = CT_OfficeStyleSheet.new_default()

    assert theme.tag == qn("a:theme")
