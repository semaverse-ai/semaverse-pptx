from __future__ import annotations

from contextlib import nullcontext as does_not_raise
from typing import Any

import pytest

from pptx.oxml.simpletypes import (
    BaseIntType,
    BaseSimpleType,
    ST_Coordinate,
    ST_HexColorRGB,
    ST_Percentage,
)


class ST_SimpleType(BaseSimpleType):
    @classmethod
    def convert_from_xml(cls, str_value: str) -> int:
        return int(str_value)

    @classmethod
    def convert_to_xml(cls, value: int) -> str:
        return str(value)

    @classmethod
    def validate(cls, value: int) -> None:
        cls.validate_int(value)


def test_base_simple_type_from_xml() -> None:
    xml_value = "42"
    value = ST_SimpleType.from_xml(xml_value)
    assert value == 42


def test_base_simple_type_to_xml() -> None:
    value = 42
    xml_value = ST_SimpleType.to_xml(value)
    assert xml_value == "42"


@pytest.mark.parametrize(
    ("value", "expected_exception"),
    [
        (42, None),
        (0, None),
        (-42, None),
        ("42", TypeError),
        (None, TypeError),
        (42.42, TypeError),
    ],
)
def test_base_simple_type_validate_int(
    value: Any, expected_exception: type[Exception] | None
) -> None:
    expectation = pytest.raises(expected_exception) if expected_exception else does_not_raise()
    with expectation:
        BaseSimpleType.validate_int(value)


@pytest.mark.parametrize(
    ("value", "expected_exception"),
    [
        ("foobar", None),
        ("", None),
        (" foo ", None),
        (("foo",), TypeError),
        (42, TypeError),
        (None, TypeError),
        (42.42, TypeError),
    ],
)
def test_base_simple_type_validate_string(
    value: Any, expected_exception: type[Exception] | None
) -> None:
    expectation = pytest.raises(expected_exception) if expected_exception else does_not_raise()
    with expectation:
        BaseSimpleType.validate_string(value)


@pytest.mark.parametrize(
    ("xml_value", "expected_value", "expected_exception"),
    [
        ("42", 42, None),
        ("-42", -42, None),
        ("-0042", -42, None),
        ("", None, ValueError),
        ("foo", None, ValueError),
        ("42.42", None, ValueError),
        ("0x0a3", None, ValueError),
        (None, None, TypeError),
    ],
)
def test_base_int_type_convert_from_xml(
    xml_value: str | None, expected_value: int | None, expected_exception: type[Exception] | None
) -> None:
    expectation = pytest.raises(expected_exception) if expected_exception else does_not_raise()
    with expectation:
        value = BaseIntType.convert_from_xml(xml_value)
        assert value == expected_value


@pytest.mark.parametrize(
    ("value", "expected_xml_value"),
    [(-42, "-42"), (0x2A, "42")],
)
def test_base_int_type_convert_to_xml(value: int, expected_xml_value: str) -> None:
    xml_value = BaseIntType.convert_to_xml(value)
    assert xml_value == expected_xml_value


@pytest.mark.parametrize(
    ("xml_value", "expected_value"),
    [
        ("1.2in", 1097280),
        ("42mm", 1512000),
        ("0024cm", 8640000),
        ("-42pt", -533400),
        ("-036.214pc", -5519014),
        ("0pi", 0),
    ],
)
def test_st_coordinate_convert_from_xml(xml_value: str, expected_value: int) -> None:
    value = ST_Coordinate.convert_from_xml(xml_value)
    assert value == expected_value


@pytest.mark.parametrize(
    ("xml_value", "expected_exception"),
    [
        ("012345", None),
        ("ABCDEF", None),
        ("deadbf", None),
        ("0A1B3C", None),
        (None, TypeError),
        (123456, TypeError),
        ("F00BAR", ValueError),
        ("F00b", ValueError),
    ],
)
def test_st_hex_color_rgb_validate(
    xml_value: str | int | None, expected_exception: type[Exception] | None
) -> None:
    expectation = pytest.raises(expected_exception) if expected_exception else does_not_raise()
    with expectation:
        ST_HexColorRGB.validate(xml_value)


@pytest.mark.parametrize(
    ("value", "expected_value"),
    [("deadbf", "DEADBF"), ("012345", "012345"), ("0a1b3c", "0A1B3C")],
)
def test_st_hex_color_rgb_convert_to_xml(value: str, expected_value: str) -> None:
    xml_value = ST_HexColorRGB.convert_to_xml(value)
    assert xml_value == expected_value


@pytest.mark.parametrize(
    ("xml_value", "expected_value"),
    [
        ("12.34%", 0.1234),
        ("42%", 0.42),
        ("024%", 0.24),
        ("-42%", -0.42),
        ("-036.214%", -0.36214),
        ("0%", 0.0),
    ],
)
def test_st_percentage_convert_from_xml(xml_value: str, expected_value: float) -> None:
    tolerance = 0.000001
    value = ST_Percentage.convert_from_xml(xml_value)
    assert abs(value - expected_value) < tolerance
