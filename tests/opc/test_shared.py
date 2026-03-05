from __future__ import annotations

import pytest

from pptx.opc.shared import CaseInsensitiveDict


def test_case_insensitive_dict_contains_handles_non_string_keys() -> None:
    mapping = CaseInsensitiveDict(xml="application/xml")

    assert "XML" in mapping
    assert None not in mapping
    assert 123 not in mapping


def test_case_insensitive_dict_getitem_raises_keyerror_for_non_string_keys() -> None:
    mapping = CaseInsensitiveDict(xml="application/xml")

    with pytest.raises(KeyError):
        _ = mapping[None]  # type: ignore[index]

    with pytest.raises(KeyError):
        _ = mapping[123]  # type: ignore[index]


def test_case_insensitive_dict_remains_case_insensitive_for_string_keys() -> None:
    mapping = CaseInsensitiveDict()

    mapping["XML"] = "application/xml"

    assert mapping["xml"] == "application/xml"
    assert mapping["Xml"] == "application/xml"
