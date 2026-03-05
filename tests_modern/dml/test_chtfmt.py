from __future__ import annotations

import pytest

from pptx.dml.chtfmt import ChartFormat
from pptx.dml.fill import FillFormat
from pptx.dml.line import LineFormat
from pptx.oxml import parse_xml
from tests_modern.xml_utils import serialize_xml


def _chart_element(tag: str, with_sp_pr: bool):
    sp_pr = "<c:spPr/>" if with_sp_pr else ""
    return parse_xml(
        (
            f'<c:{tag} xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
            f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">{sp_pr}</c:{tag}>'
        ).encode("utf-8")
    )


@pytest.mark.parametrize("tag", ["catAx", "dPt", "majorGridlines", "valAx"])
def test_chart_format_fill_returns_fill_format_and_creates_sppr(tag: str) -> None:
    # Arrange
    element = _chart_element(tag=tag, with_sp_pr=False)
    chart_format = ChartFormat(element)

    # Act
    fill = chart_format.fill

    # Assert
    assert isinstance(fill, FillFormat)
    assert element.spPr is not None


def test_chart_format_line_returns_line_format_and_reuses_existing_sppr() -> None:
    # Arrange
    element = _chart_element(tag="catAx", with_sp_pr=True)
    original_xml = serialize_xml(element)
    chart_format = ChartFormat(element)

    # Act
    line = chart_format.line

    # Assert
    assert isinstance(line, LineFormat)
    assert serialize_xml(element) == original_xml
