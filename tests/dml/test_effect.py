from __future__ import annotations

import pytest

from pptx.dml.effect import ShadowFormat
from pptx.oxml import parse_xml


def _sp_pr(has_effect_list: bool, group: bool = False):
    tag = "p:grpSpPr" if group else "p:spPr"
    child = "<a:effectLst/>" if has_effect_list else ""
    return parse_xml(
        (
            f'<{tag} xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
            f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">{child}</{tag}>'
        ).encode("utf-8")
    )


@pytest.mark.parametrize(
    ("group", "has_effect_list", "expected"),
    [
        (False, False, True),
        (False, True, False),
        (True, False, True),
        (True, True, False),
    ],
)
def test_shadow_format_inherit_getter(
    group: bool, has_effect_list: bool, expected: bool
) -> None:
    # Arrange
    shadow = ShadowFormat(_sp_pr(has_effect_list=has_effect_list, group=group))

    # Act
    inherit = shadow.inherit

    # Assert
    assert inherit is expected


@pytest.mark.parametrize(
    ("initial_has_effect_list", "value", "expected_has_effect_list"),
    [
        (False, False, True),
        (True, False, True),
        (False, True, False),
        (True, True, False),
    ],
)
def test_shadow_format_inherit_setter(
    initial_has_effect_list: bool, value: bool, expected_has_effect_list: bool
) -> None:
    # Arrange
    sp_pr = _sp_pr(has_effect_list=initial_has_effect_list, group=False)
    shadow = ShadowFormat(sp_pr)

    # Act
    shadow.inherit = value

    # Assert
    assert (sp_pr.effectLst is not None) is expected_has_effect_list
