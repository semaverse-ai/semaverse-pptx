from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO


@dataclass
class GraphicFrameProxy:
    width: int = 0
    height: int = 0
    part: object | None = None


@dataclass
class ParentProxy:
    part: object


@dataclass
class PresentationPartStub:
    content_type: str = ""
    presentation: object | None = None
    core_properties: object = "core-props"
    notes_master: object = "notes-master"
    saved_payload: bytes | None = None
    renamed_rids: list[str] = field(default_factory=list)
    slides_by_rid: dict[str, object] = field(default_factory=dict)
    slide_masters_by_rid: dict[str, object] = field(default_factory=dict)

    def save(self, file: BytesIO) -> None:
        payload = b"saved"
        file.write(payload)
        self.saved_payload = payload

    def rename_slide_parts(self, rids: list[str]) -> None:
        self.renamed_rids = list(rids)

    def related_slide(self, rid: str) -> object:
        return self.slides_by_rid[rid]

    def related_slide_master(self, rid: str) -> object:
        return self.slide_masters_by_rid[rid]


@dataclass
class PackageStub:
    main_document_part: PresentationPartStub


@dataclass
class SlidePartStub:
    has_notes_slide: bool = True
    slide_id: int = 256
    slide_layout: object = "layout"
    notes_slide: object = "notes"


@dataclass
class SlidesPartStub:
    slides_by_rid: dict[str, object]
    slide_by_id: dict[int, object]
    add_slide_result: tuple[str, object]

    def related_slide(self, rid: str) -> object:
        return self.slides_by_rid[rid]

    def get_slide(self, slide_id: int) -> object | None:
        return self.slide_by_id.get(slide_id)

    def add_slide(self, slide_layout: object) -> tuple[str, object]:
        return self.add_slide_result


@dataclass
class CloneRecorder:
    cloned_with: list[object] = field(default_factory=list)

    def clone_layout_placeholders(self, slide_layout: object) -> None:
        self.cloned_with.append(slide_layout)


@dataclass
class NewSlideStub:
    shapes: CloneRecorder
