from __future__ import annotations

import pytest

from pptx.util import Centipoints, Cm, Emu, Inches, Length, Mm, Pt, lazyproperty


@pytest.mark.parametrize(
    ("unit_cls", "units_val", "expected_emu"),
    [
        (Length, 914400, 914400),
        (Inches, 1.1, 1005840),
        (Centipoints, 12.5, 1587),
        (Cm, 2.53, 910799),
        (Emu, 9144.9, 9144),
        (Mm, 13.8, 496800),
        (Pt, 24.5, 311150),
    ],
)
def test_length_constructs_from_convenient_units(
    unit_cls: type[Length], units_val: float, expected_emu: int
) -> None:
    length = unit_cls(units_val)

    assert isinstance(length, Length)
    assert length == expected_emu


@pytest.mark.parametrize(
    ("emu", "units_prop_name", "expected_length_in_units"),
    [
        (914400, "inches", 1.0),
        (914400, "centipoints", 7200.0),
        (914400, "cm", 2.54),
        (914400, "emu", 914400),
        (914400, "mm", 25.4),
        (914400, "pt", 72.0),
    ],
)
def test_length_self_converts_to_convenient_units(
    emu: int, units_prop_name: str, expected_length_in_units: float
) -> None:
    length = Length(emu)

    length_in_units = getattr(length, units_prop_name)

    assert length_in_units == expected_length_in_units


def test_lazyproperty_evaluates_once_and_caches_result() -> None:
    class Example:
        def __init__(self) -> None:
            self.calls = 0

        @lazyproperty
        def value(self) -> int:
            self.calls += 1
            return self.calls

    example = Example()

    assert example.value == 1
    assert example.value == 1
    assert example.calls == 1


def test_lazyproperty_accessed_on_class_returns_descriptor() -> None:
    class Example:
        @lazyproperty
        def value(self) -> int:
            return 42

    assert isinstance(Example.value, lazyproperty)


def test_lazyproperty_is_read_only() -> None:
    class Example:
        @lazyproperty
        def value(self) -> int:
            return 42

    example = Example()

    with pytest.raises(AttributeError, match="can't set attribute"):
        example.value = 24
