from __future__ import annotations

import pytest

from pptx.enum.shapes import PROG_ID


def test_prog_id_has_members_for_known_ole_embeddings() -> None:
    assert PROG_ID.DOCX
    assert PROG_ID.PPTX
    assert PROG_ID.XLSX


@pytest.mark.parametrize(
    ("member", "expected_value"),
    [(PROG_ID.DOCX, 609600), (PROG_ID.PPTX, 609600), (PROG_ID.XLSX, 609600)],
)
def test_prog_id_knows_height(member: PROG_ID, expected_value: int) -> None:
    assert member.height == expected_value


def test_prog_id_knows_icon_filename() -> None:
    assert PROG_ID.DOCX.icon_filename == "docx-icon.emf"


def test_prog_id_knows_prog_id() -> None:
    assert PROG_ID.PPTX.progId == "PowerPoint.Show.12"


def test_prog_id_knows_width() -> None:
    assert PROG_ID.XLSX.width == 965200


@pytest.mark.parametrize(
    ("value", "expected_value"),
    [
        (PROG_ID.DOCX, True),
        (PROG_ID.PPTX, True),
        (PROG_ID.XLSX, True),
        (17, False),
        ("XLSX", False),
    ],
)
def test_prog_id_knows_each_member_is_an_instance(value: object, expected_value: bool) -> None:
    assert isinstance(value, PROG_ID) is expected_value
