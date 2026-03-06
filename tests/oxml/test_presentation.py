from __future__ import annotations

import pytest

from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls


def test_ct_slide_id_list_add_sld_id() -> None:
    sld_id_list = parse_xml(
        f'<p:sldIdLst {nsdecls("p", "r")}><p:sldId r:id="rId4" id="256"/></p:sldIdLst>'
    )

    sld_id_list.add_sldId("rId1")

    assert len(sld_id_list.sldId_lst) == 2
    assert sld_id_list.sldId_lst[1].rId == "rId1"
    assert sld_id_list.sldId_lst[1].id == 257


@pytest.mark.parametrize(
    ("xml_body", "expected_value"),
    [
        ("", 256),
        ('<p:sldId id="42"/>', 256),
        ('<p:sldId id="256"/>', 257),
        ('<p:sldId id="256"/><p:sldId id="712"/>', 713),
        ('<p:sldId id="280"/><p:sldId id="257"/>', 281),
        ('<p:sldId id="2147483646"/>', 2147483647),
        ('<p:sldId id="2147483647"/>', 256),
        ('<p:sldId id="2147483648"/>', 256),
        ('<p:sldId id="256"/><p:sldId id="2147483647"/>', 257),
        ('<p:sldId id="256"/><p:sldId id="2147483647"/><p:sldId id="257"/>', 258),
        ('<p:sldId id="245"/><p:sldId id="2147483647"/><p:sldId id="256"/>', 257),
    ],
)
def test_ct_slide_id_list_next_id(xml_body: str, expected_value: int) -> None:
    sld_id_list = parse_xml(f"<p:sldIdLst {nsdecls('p')}>{xml_body}</p:sldIdLst>")

    next_id = sld_id_list._next_id

    assert 256 <= next_id <= 2147483647
    assert next_id == expected_value
