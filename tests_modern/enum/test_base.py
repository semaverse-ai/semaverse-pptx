from __future__ import annotations

import pytest

from pptx.enum.action import PP_ACTION, PP_ACTION_TYPE
from pptx.enum.base import DocsPageFormatter
from pptx.enum.dml import MSO_LINE_DASH_STYLE


def test_base_enum_members_are_equivalent_to_integer_value() -> None:
    assert PP_ACTION_TYPE.END_SHOW == 6
    assert PP_ACTION_TYPE.NONE == 0


def test_base_enum_member_repr_includes_enum_and_member_name() -> None:
    assert repr(PP_ACTION_TYPE.END_SHOW) == "<PP_ACTION_TYPE.END_SHOW: 6>"
    assert repr(PP_ACTION_TYPE.RUN_MACRO) == "<PP_ACTION_TYPE.RUN_MACRO: 8>"


def test_base_enum_member_str_includes_name_and_integer_value() -> None:
    assert str(PP_ACTION_TYPE.FIRST_SLIDE) == "FIRST_SLIDE (3)"
    assert str(PP_ACTION_TYPE.HYPERLINK) == "HYPERLINK (7)"


def test_base_enum_provides_docstring_for_each_member() -> None:
    assert PP_ACTION_TYPE.LAST_SLIDE.__doc__ == "Moves to the last slide."
    assert PP_ACTION_TYPE.LAST_SLIDE_VIEWED.__doc__ == "Moves to the last slide viewed."


def test_base_enum_looks_up_member_by_value() -> None:
    assert PP_ACTION_TYPE(10) == PP_ACTION_TYPE.NAMED_SLIDE_SHOW
    assert PP_ACTION_TYPE(101) == PP_ACTION_TYPE.NAMED_SLIDE


def test_base_enum_raises_when_no_member_has_value() -> None:
    with pytest.raises(ValueError, match="42 is not a valid PP_ACTION_TYPE"):
        PP_ACTION_TYPE(42)


def test_base_enum_knows_its_name() -> None:
    assert PP_ACTION_TYPE.NEXT_SLIDE.name == "NEXT_SLIDE"
    assert PP_ACTION_TYPE.NONE.name == "NONE"


def test_base_enum_alias_refers_to_same_member() -> None:
    assert PP_ACTION_TYPE.OPEN_FILE is PP_ACTION.OPEN_FILE


def test_base_xml_enum_looks_up_member_by_xml_attribute_value() -> None:
    assert MSO_LINE_DASH_STYLE.from_xml("dash") == MSO_LINE_DASH_STYLE.DASH
    assert MSO_LINE_DASH_STYLE.from_xml("dashDot") == MSO_LINE_DASH_STYLE.DASH_DOT


def test_base_xml_enum_raises_on_unregistered_xml_attribute_value() -> None:
    with pytest.raises(ValueError, match="MSO_LINE_DASH_STYLE has no XML mapping for 'wavy'"):
        MSO_LINE_DASH_STYLE.from_xml("wavy")


def test_base_xml_enum_empty_string_never_maps_to_member() -> None:
    with pytest.raises(ValueError, match="MSO_LINE_DASH_STYLE has no XML mapping for ''"):
        MSO_LINE_DASH_STYLE.from_xml("")


def test_base_xml_enum_knows_xml_attribute_value_for_each_member() -> None:
    assert MSO_LINE_DASH_STYLE.to_xml(MSO_LINE_DASH_STYLE.SOLID) == "solid"


def test_base_xml_enum_maps_int_to_member_before_xml_mapping() -> None:
    assert MSO_LINE_DASH_STYLE.to_xml(3) == "sysDot"


def test_base_xml_enum_raises_when_int_has_no_member() -> None:
    with pytest.raises(ValueError, match="42 is not a valid MSO_LINE_DASH_STYLE"):
        MSO_LINE_DASH_STYLE.to_xml(42)


def test_base_xml_enum_raises_when_member_has_no_xml_value() -> None:
    with pytest.raises(ValueError, match="MSO_LINE_DASH_STYLE.DASH_STYLE_MIXED has no XML r"):
        MSO_LINE_DASH_STYLE.to_xml(-2)


def test_docs_page_formatter_composes_page_string() -> None:
    clsdict = {
        "__ms_name__": "MSO_FAKE_ENUM",
        "__doc__": "Fake enum for testing.",
        "__members__": [PP_ACTION_TYPE.NONE, PP_ACTION_TYPE.END_SHOW],
    }

    page_str = DocsPageFormatter("MSO_FAKE_ENUM", clsdict).page_str

    assert ".. _MSO_FAKE_ENUM:" in page_str
    assert "``MSO_FAKE_ENUM``" in page_str
    assert "Fake enum for testing." in page_str
    assert "NONE" in page_str
    assert "END_SHOW" in page_str


@pytest.mark.parametrize("docstring", [None, ""])
def test_docs_page_formatter_uses_empty_intro_text_when_docstring_missing_or_none(
    docstring: str | None,
) -> None:
    clsdict = {"__ms_name__": "MSO_FAKE_ENUM", "__doc__": docstring, "__members__": []}

    intro_text = DocsPageFormatter("MSO_FAKE_ENUM", clsdict)._intro_text

    assert intro_text == ""
