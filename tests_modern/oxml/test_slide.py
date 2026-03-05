from __future__ import annotations

from syrupy.assertion import SnapshotAssertion

from pptx.oxml.slide import CT_NotesMaster, CT_NotesSlide


def test_ct_notes_master_new_default(snapshot: SnapshotAssertion) -> None:
    notes_master = CT_NotesMaster.new_default()

    assert str(notes_master.xml) == snapshot


def test_ct_notes_slide_new(snapshot: SnapshotAssertion) -> None:
    notes = CT_NotesSlide.new()

    assert str(notes.xml) == snapshot
