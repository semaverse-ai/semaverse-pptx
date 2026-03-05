from __future__ import annotations

from pptx.oxml.ns import qn
from pptx.oxml.slide import CT_NotesMaster, CT_NotesSlide


def test_ct_notes_master_new_default() -> None:
    notes_master = CT_NotesMaster.new_default()

    assert notes_master.tag == qn("p:notesMaster")


def test_ct_notes_slide_new() -> None:
    notes = CT_NotesSlide.new()

    assert notes.tag == qn("p:notes")
