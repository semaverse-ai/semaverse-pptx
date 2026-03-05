from __future__ import annotations

from pptx.chart.legend import Legend
from pptx.enum.chart import XL_LEGEND_POSITION
from pptx.oxml import parse_xml
from pptx.text.text import Font


def test_legend_properties() -> None:
    legend = Legend(
        parse_xml(b'<c:legend xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"/>')
    )

    assert legend.horz_offset == 0.0
    assert legend.include_in_layout is True
    assert legend.position == XL_LEGEND_POSITION.RIGHT
    assert isinstance(legend.font, Font)

    legend.horz_offset = 0.33
    legend.include_in_layout = False
    legend.position = XL_LEGEND_POSITION.BOTTOM

    assert legend.horz_offset == 0.33
    assert legend.include_in_layout is False
    assert legend.position == XL_LEGEND_POSITION.BOTTOM
