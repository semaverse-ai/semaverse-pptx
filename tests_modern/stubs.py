from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GraphicFrameProxy:
    width: int = 0
    height: int = 0
    part: object | None = None
