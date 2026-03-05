from __future__ import annotations

import pytest

from pptx.enum.shapes import PROG_ID
from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.packuri import PackURI
from pptx.package import Package
from pptx.parts.embeddedpackage import (
    EmbeddedDocxPart,
    EmbeddedPackagePart,
    EmbeddedPptxPart,
    EmbeddedXlsxPart,
)


class _TestPackage(Package):
    def next_partname(self, tmpl: str) -> PackURI:
        return PackURI(tmpl % 1)


@pytest.fixture
def package() -> Package:
    return _TestPackage(None)


@pytest.mark.parametrize(
    ("prog_id", "expected_class", "expected_content_type", "expected_partname"),
    [
        (
            PROG_ID.DOCX,
            EmbeddedDocxPart,
            CT.WML_DOCUMENT,
            "/ppt/embeddings/Microsoft_Word_Document1.docx",
        ),
        (
            PROG_ID.PPTX,
            EmbeddedPptxPart,
            CT.PML_PRESENTATION,
            "/ppt/embeddings/Microsoft_PowerPoint_Presentation1.pptx",
        ),
        (
            PROG_ID.XLSX,
            EmbeddedXlsxPart,
            CT.SML_SHEET,
            "/ppt/embeddings/Microsoft_Excel_Sheet1.xlsx",
        ),
        (
            "Foo.Bar.42",
            EmbeddedPackagePart,
            CT.OFC_OLE_OBJECT,
            "/ppt/embeddings/oleObject1.bin",
        ),
    ],
)
def test_embedded_package_part_factory(
    package: Package,
    prog_id: PROG_ID | str,
    expected_class: type[EmbeddedPackagePart],
    expected_content_type: str,
    expected_partname: str,
) -> None:
    blob = b"0123456789"

    part = EmbeddedPackagePart.factory(prog_id, blob, package)

    assert isinstance(part, expected_class)
    assert part.blob == blob
    assert part.content_type == expected_content_type
    assert part.partname == expected_partname
