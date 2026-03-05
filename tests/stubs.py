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


@dataclass
class _SlidesProxy:
    slides: list[object]


@dataclass
class _PresentationPartProxy:
    presentation: _SlidesProxy


@dataclass
class _PackageProxy:
    presentation_part: _PresentationPartProxy


@dataclass
class RelatedSlidePartStub:
    slide: object


@dataclass
class SlideTargetStub:
    part: object


@dataclass
class ActionPartStub:
    slide: object | None = None
    slides: list[object] = field(default_factory=list)
    relate_to_rid: str = "rId3"
    target_refs_by_rid: dict[str, str] = field(default_factory=dict)
    related_parts_by_rid: dict[str, object] = field(default_factory=dict)
    dropped_rids: list[str] = field(default_factory=list)
    relate_to_calls: list[tuple[object, str, bool]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.package = _PackageProxy(_PresentationPartProxy(_SlidesProxy(self.slides)))

    def drop_rel(self, rid: str) -> None:
        self.dropped_rids.append(rid)

    def relate_to(self, target: object, reltype: str, is_external: bool = False) -> str:
        self.relate_to_calls.append((target, reltype, is_external))
        return self.relate_to_rid

    def related_part(self, rid: str) -> object:
        return self.related_parts_by_rid[rid]

    def target_ref(self, rid: str) -> str:
        return self.target_refs_by_rid[rid]


@dataclass
class NotesMasterPartProxy:
    notes_master: object


@dataclass
class SlidePartProxy:
    slide: object


@dataclass
class SlideMasterPartProxy:
    slide_master: object


@dataclass
class SlideLayoutPartProxy:
    slide_layout: object


@dataclass
class CorePropertiesPackageStub:
    core_properties: object


@dataclass
class SaveCallPackageStub:
    saved_paths: list[str] = field(default_factory=list)

    def save(self, path_or_stream: str) -> None:
        self.saved_paths.append(path_or_stream)


@dataclass
class NotesSlideCloneProxy:
    clone_calls: list[object] = field(default_factory=list)

    def clone_master_placeholders(self, notes_master: object) -> None:
        self.clone_calls.append(notes_master)


@dataclass
class NotesSlidePartProxy:
    notes_slide: NotesSlideCloneProxy


@dataclass
class PresentationPartNotesMasterProxy:
    notes_master_part: object


@dataclass
class PackagePresentationProxy:
    presentation_part: PresentationPartNotesMasterProxy


@dataclass
class SlideIdPresentationPartProxy:
    slide_id_value: int

    def slide_id(self, _slide_part: object) -> int:
        return self.slide_id_value


@dataclass
class PackageWithPresentationPartProxy:
    presentation_part: SlideIdPresentationPartProxy
