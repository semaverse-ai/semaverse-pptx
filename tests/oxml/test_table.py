from __future__ import annotations

import pytest

from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pptx.oxml.table import CT_Table, TcRange


def _tbl(xml_body: str) -> CT_Table:
    return parse_xml(f"<a:tbl {nsdecls('a')}>{xml_body}</a:tbl>")


def test_ct_table_new_tbl() -> None:
    table = CT_Table.new_tbl(2, 3, 334, 445)

    assert len(table.tr_lst) == 2
    assert len(table.tr_lst[0].tc_lst) == 3


def test_ct_table_tc() -> None:
    table = _tbl(
        "<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr><a:tr><a:tc id='10'/><a:tc id='11'/></a:tr>"
    )
    cells = table.xpath("//a:tc")

    assert table.tc(0, 0) is cells[0]
    assert table.tc(0, 1) is cells[1]
    assert table.tc(1, 0) is cells[2]
    assert table.tc(1, 1) is cells[3]


@pytest.mark.parametrize(
    ("xml_body", "expected_value"),
    [
        ("<a:tr><a:tc/><a:tc/></a:tr>", False),
        ('<a:tr><a:tc gridSpan="1"/><a:tc hMerge="false"/></a:tr>', False),
        ('<a:tr><a:tc gridSpan="2"/><a:tc hMerge="1"/></a:tr>', True),
        ("<a:tr><a:tc/></a:tr><a:tr><a:tc/></a:tr>", False),
        ('<a:tr><a:tc rowSpan="1"/></a:tr><a:tr><a:tc vMerge="false"/></a:tr>', False),
        ('<a:tr><a:tc rowSpan="2"/></a:tr><a:tr><a:tc vMerge="true"/></a:tr>', True),
    ],
)
def test_tc_range_contains_merged_cell(xml_body: str, expected_value: bool) -> None:
    tcs = _tbl(xml_body).xpath("//a:tc")
    tc_range = TcRange(tcs[0], tcs[1])

    contains_merged_cell = tc_range.contains_merged_cell

    assert contains_merged_cell is expected_value


@pytest.mark.parametrize(
    ("xml_body", "expected_value"),
    [
        ("<a:tr><a:tc/><a:tc/></a:tr>", (1, 2)),
        ("<a:tr><a:tc/></a:tr><a:tr><a:tc/></a:tr>", (2, 1)),
        ("<a:tr><a:tc/><a:tc/></a:tr><a:tr><a:tc/><a:tc/></a:tr>", (2, 2)),
    ],
)
def test_tc_range_dimensions(xml_body: str, expected_value: tuple[int, int]) -> None:
    tcs = _tbl(xml_body).xpath("//a:tc")
    tc_range = TcRange(tcs[0], tcs[-1])

    dimensions = tc_range.dimensions

    assert dimensions == expected_value


def test_tc_range_in_same_table() -> None:
    table = _tbl("<a:tr><a:tc/><a:tc/></a:tr>")
    other_table = _tbl("<a:tr><a:tc/><a:tc/></a:tr>")
    tc = table.xpath("//a:tc")[0]
    other_tc = table.xpath("//a:tc")[1]
    off_table_tc = other_table.xpath("//a:tc")[1]

    assert TcRange(tc, other_tc).in_same_table is True
    assert TcRange(tc, off_table_tc).in_same_table is False


@pytest.mark.parametrize(
    ("xml_body", "start_idx", "end_idx", "expected_ids"),
    [
        ("<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>", 0, 1, ["01"]),
        ("<a:tr><a:tc id='00'/></a:tr><a:tr><a:tc id='10'/></a:tr>", 0, 1, []),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/></a:tr>",
            2,
            1,
            ["01", "11"],
        ),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/><a:tc id='02'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/><a:tc id='12'/></a:tr>"
            "<a:tr><a:tc id='20'/><a:tc id='21'/><a:tc id='22'/></a:tr>",
            0,
            8,
            ["01", "02", "11", "12", "21", "22"],
        ),
    ],
)
def test_tc_range_iter_except_left_col_tcs(
    xml_body: str, start_idx: int, end_idx: int, expected_ids: list[str]
) -> None:
    table = _tbl(xml_body)
    tcs = table.xpath("//a:tc")
    tc_range = TcRange(tcs[start_idx], tcs[end_idx])

    tc_ids = [tc.get("id") for tc in tc_range.iter_except_left_col_tcs()]

    assert tc_ids == expected_ids


@pytest.mark.parametrize(
    ("xml_body", "start_idx", "end_idx", "expected_ids"),
    [
        ("<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>", 0, 1, []),
        ("<a:tr><a:tc id='00'/></a:tr><a:tr><a:tc id='10'/></a:tr>", 0, 1, ["10"]),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/></a:tr>",
            2,
            1,
            ["10", "11"],
        ),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/><a:tc id='02'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/><a:tc id='12'/></a:tr>"
            "<a:tr><a:tc id='20'/><a:tc id='21'/><a:tc id='22'/></a:tr>",
            0,
            8,
            ["10", "11", "12", "20", "21", "22"],
        ),
    ],
)
def test_tc_range_iter_except_top_row_tcs(
    xml_body: str, start_idx: int, end_idx: int, expected_ids: list[str]
) -> None:
    table = _tbl(xml_body)
    tcs = table.xpath("//a:tc")
    tc_range = TcRange(tcs[start_idx], tcs[end_idx])

    tc_ids = [tc.get("id") for tc in tc_range.iter_except_top_row_tcs()]

    assert tc_ids == expected_ids


@pytest.mark.parametrize(
    ("xml_body", "start_idx", "end_idx", "expected_ids"),
    [
        ("<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>", 0, 1, ["00"]),
        ("<a:tr><a:tc id='00'/></a:tr><a:tr><a:tc id='10'/></a:tr>", 0, 1, ["00", "10"]),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/></a:tr>",
            2,
            1,
            ["00", "10"],
        ),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/><a:tc id='02'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/><a:tc id='12'/></a:tr>"
            "<a:tr><a:tc id='20'/><a:tc id='21'/><a:tc id='22'/></a:tr>",
            4,
            8,
            ["11", "21"],
        ),
    ],
)
def test_tc_range_iter_left_col_tcs(
    xml_body: str, start_idx: int, end_idx: int, expected_ids: list[str]
) -> None:
    table = _tbl(xml_body)
    tcs = table.xpath("//a:tc")
    tc_range = TcRange(tcs[start_idx], tcs[end_idx])

    tc_ids = [tc.get("id") for tc in tc_range.iter_left_col_tcs()]

    assert tc_ids == expected_ids


@pytest.mark.parametrize(
    ("xml_body", "start_idx", "end_idx", "expected_ids"),
    [
        ("<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>", 0, 1, ["00", "01"]),
        ("<a:tr><a:tc id='00'/></a:tr><a:tr><a:tc id='10'/></a:tr>", 0, 1, ["00"]),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/></a:tr>",
            2,
            1,
            ["00", "01"],
        ),
        (
            "<a:tr><a:tc id='00'/><a:tc id='01'/><a:tc id='02'/></a:tr>"
            "<a:tr><a:tc id='10'/><a:tc id='11'/><a:tc id='12'/></a:tr>"
            "<a:tr><a:tc id='20'/><a:tc id='21'/><a:tc id='22'/></a:tr>",
            4,
            8,
            ["11", "12"],
        ),
    ],
)
def test_tc_range_iter_top_row_tcs(
    xml_body: str, start_idx: int, end_idx: int, expected_ids: list[str]
) -> None:
    table = _tbl(xml_body)
    tcs = table.xpath("//a:tc")
    tc_range = TcRange(tcs[start_idx], tcs[end_idx])

    tc_ids = [tc.get("id") for tc in tc_range.iter_top_row_tcs()]

    assert tc_ids == expected_ids


@pytest.mark.parametrize(
    ("xml_body", "expected_origin_text"),
    [
        (
            "<a:tr>"
            "<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>a</a:t></a:r></a:p></a:txBody></a:tc>"
            "<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>b</a:t></a:r></a:p></a:txBody></a:tc>"
            "</a:tr>",
            "a\nb",
        ),
        (
            "<a:tr>"
            "<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p/></a:txBody></a:tc>"
            "<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>second</a:t></a:r></a:p></a:txBody></a:tc>"
            "</a:tr>",
            "second",
        ),
    ],
)
def test_tc_range_move_content_to_origin(
    xml_body: str, expected_origin_text: str
) -> None:
    table = _tbl(xml_body)
    tcs = table.xpath("//a:tc")
    tc_range = TcRange(tcs[0], tcs[1])

    tc_range.move_content_to_origin()

    assert tcs[0].text == expected_origin_text
    assert tcs[1].text == ""
