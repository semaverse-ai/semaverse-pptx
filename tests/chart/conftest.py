from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass
class ChartWorkbookStub:
    updated_blob: bytes | None = None

    def update_from_xlsx_blob(self, blob: bytes) -> None:
        self.updated_blob = blob


@dataclass
class ChartPartStub:
    chart_workbook: ChartWorkbookStub


@pytest.fixture
def chart_part_stub() -> ChartPartStub:
    return ChartPartStub(chart_workbook=ChartWorkbookStub())
