from __future__ import annotations

from pptx.chart.marker import Marker
from pptx.dml.chtfmt import ChartFormat
from pptx.enum.chart import XL_MARKER_STYLE
from pptx.oxml import parse_xml


def test_marker_properties() -> None:
    marker = Marker(
        parse_xml(b'<c:ser xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"/>')
    )

    assert marker.size is None
    assert marker.style is None

    marker.size = 24
    marker.style = XL_MARKER_STYLE.CIRCLE

    assert marker.size == 24
    assert marker.style == XL_MARKER_STYLE.CIRCLE
    assert isinstance(marker.format, ChartFormat)
