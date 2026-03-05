from __future__ import annotations

from dataclasses import dataclass, field

import pytest


@dataclass
class DummyPart:
    rel_counter: int = 0
    rel_targets: dict[str, str] = field(default_factory=dict)
    dropped: set[str] = field(default_factory=set)

    def relate_to(self, target: str, reltype: str, is_external: bool = False) -> str:
        self.rel_counter += 1
        rel_id = f"rId{self.rel_counter}"
        self.rel_targets[rel_id] = target
        return rel_id

    def target_ref(self, rel_id: str) -> str | None:
        return self.rel_targets.get(rel_id)

    def drop_rel(self, rel_id: str) -> None:
        self.dropped.add(rel_id)
        self.rel_targets.pop(rel_id, None)


@dataclass
class DummyParent:
    part: DummyPart


@dataclass
class FitParent(DummyParent):
    width: int = 914400
    height: int = 914400


@pytest.fixture
def dummy_part() -> DummyPart:
    return DummyPart()


@pytest.fixture
def text_parent(dummy_part: DummyPart) -> DummyParent:
    return DummyParent(dummy_part)


@pytest.fixture
def fit_parent(dummy_part: DummyPart) -> FitParent:
    return FitParent(part=dummy_part, width=1828800, height=1828800)
