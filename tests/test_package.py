from __future__ import annotations

from dataclasses import dataclass

import pytest

from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.package import Package, _ImageParts, _MediaParts
from pptx.parts.image import Image, ImagePart
from pptx.parts.media import MediaPart


@dataclass
class _RelStub:
    is_external: bool
    reltype: str
    target_part: object


@dataclass
class _ShaPartStub:
    partname: PackURI
    sha1: str | None = None


@dataclass
class _MediaStub:
    sha1: str


@dataclass
class _NoShaPartStub:
    partname: PackURI


def test_package_core_properties_returns_existing_related_part(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = Package(None)
    expected = object()
    monkeypatch.setattr(package, "part_related_by", lambda reltype: expected)

    core_props = package.core_properties

    assert core_props is expected


def test_package_core_properties_creates_part_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    package = Package(None)
    created = object()
    calls: list[tuple[object, str]] = []

    def fake_part_related_by(reltype: str):
        raise KeyError

    def fake_relate_to(part: object, reltype: str) -> None:
        calls.append((part, reltype))

    monkeypatch.setattr(package, "part_related_by", fake_part_related_by)
    monkeypatch.setattr(package, "relate_to", fake_relate_to)
    monkeypatch.setattr("pptx.package.CorePropertiesPart.default", lambda pkg: created)

    core_props = package.core_properties

    assert core_props is created
    assert calls == [(created, RT.CORE_PROPERTIES)]


@pytest.mark.parametrize(
    ("existing_partnames", "expected"),
    [
        (["/ppt/media/image2.png", "/ppt/media/image4.jpg"], "/ppt/media/image1.png"),
        (["/ppt/media/image1.png", "/ppt/media/image2.jpg"], "/ppt/media/image3.png"),
    ],
)
def test_package_next_image_partname(existing_partnames: list[str], expected: str) -> None:
    package = Package(None)
    parts = [_ShaPartStub(PackURI(name)) for name in existing_partnames]
    package.iter_parts = lambda: iter(parts)  # type: ignore[method-assign]

    partname = package.next_image_partname("png")

    assert partname == expected


@pytest.mark.parametrize(
    ("existing_partnames", "expected"),
    [
        (["/ppt/media/media2.mp4", "/ppt/media/media4.mp4"], "/ppt/media/media1.mp4"),
        (["/ppt/media/media1.mp4", "/ppt/media/media2.mp4"], "/ppt/media/media3.mp4"),
    ],
)
def test_package_next_media_partname(existing_partnames: list[str], expected: str) -> None:
    package = Package(None)
    parts = [_ShaPartStub(PackURI(name)) for name in existing_partnames]
    package.iter_parts = lambda: iter(parts)  # type: ignore[method-assign]

    partname = package.next_media_partname("mp4")

    assert partname == expected


def test_package_presentation_part_delegates_to_main_document_part(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = Package(None)
    expected = object()
    monkeypatch.setattr(package, "part_related_by", lambda reltype: expected)

    presentation_part = package.presentation_part

    assert presentation_part is expected


def test_image_parts_iteration_filters_external_non_image_and_duplicates() -> None:
    package = Package(None)
    image_part = _ShaPartStub(PackURI("/ppt/media/image1.png"), sha1="abc")
    rels = [
        _RelStub(True, RT.IMAGE, image_part),
        _RelStub(False, RT.SLIDE, image_part),
        _RelStub(False, RT.IMAGE, image_part),
        _RelStub(False, RT.IMAGE, image_part),
    ]
    package.iter_rels = lambda: iter(rels)  # type: ignore[method-assign]

    image_parts = list(_ImageParts(package))

    assert image_parts == [image_part]


def test_image_parts_get_or_add_reuses_existing(monkeypatch: pytest.MonkeyPatch) -> None:
    package = Package(None)
    image_parts = _ImageParts(package)
    image = _MediaStub("abc")
    existing = object()
    monkeypatch.setattr(Image, "from_file", lambda _: image)
    monkeypatch.setattr(image_parts, "_find_by_sha1", lambda _: existing)

    image_part = image_parts.get_or_add_image_part("image.png")

    assert image_part is existing


def test_image_parts_get_or_add_creates_new_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    package = Package(None)
    image_parts = _ImageParts(package)
    image = _MediaStub("abc")
    created = object()
    monkeypatch.setattr(Image, "from_file", lambda _: image)
    monkeypatch.setattr(image_parts, "_find_by_sha1", lambda _: None)
    monkeypatch.setattr(ImagePart, "new", lambda pkg, img: created)

    image_part = image_parts.get_or_add_image_part("image.png")

    assert image_part is created


def test_image_parts_find_by_sha1_skips_parts_without_sha1() -> None:
    image_part = _ShaPartStub(PackURI("/ppt/media/image1.png"), sha1="target")
    no_sha_part = _NoShaPartStub(PackURI("/ppt/media/image2.svg"))
    rels = [
        _RelStub(False, RT.IMAGE, no_sha_part),
        _RelStub(False, RT.IMAGE, image_part),
    ]

    @dataclass
    class _PackageIterRelsStub:
        rels: list[_RelStub]

        def iter_rels(self):
            return iter(self.rels)

    image_parts = _ImageParts(_PackageIterRelsStub(rels))

    found = image_parts._find_by_sha1("target")

    assert found is image_part


def test_media_parts_iteration_filters_and_dedupes() -> None:
    package = Package(None)
    media_part = _ShaPartStub(PackURI("/ppt/media/media1.mp4"), sha1="abc")
    rels = [
        _RelStub(True, RT.MEDIA, media_part),
        _RelStub(False, RT.SLIDE, media_part),
        _RelStub(False, RT.MEDIA, media_part),
        _RelStub(False, RT.VIDEO, media_part),
    ]
    package.iter_rels = lambda: iter(rels)  # type: ignore[method-assign]

    media_parts = list(_MediaParts(package))

    assert media_parts == [media_part]


def test_media_parts_get_or_add_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    package = Package(None)
    media_parts = _MediaParts(package)
    media = _MediaStub("abc")
    existing = object()
    created = object()
    monkeypatch.setattr(media_parts, "_find_by_sha1", lambda _: existing)

    reused = media_parts.get_or_add_media_part(media)

    assert reused is existing

    monkeypatch.setattr(media_parts, "_find_by_sha1", lambda _: None)
    monkeypatch.setattr(MediaPart, "new", lambda pkg, m: created)

    new = media_parts.get_or_add_media_part(media)

    assert new is created


def test_media_parts_find_by_sha1_returns_match_or_none(monkeypatch: pytest.MonkeyPatch) -> None:
    package = Package(None)
    media_parts = _MediaParts(package)
    target = _ShaPartStub(PackURI("/ppt/media/media1.mp4"), sha1="target")
    other = _ShaPartStub(PackURI("/ppt/media/media2.mp4"), sha1="other")
    monkeypatch.setattr(_MediaParts, "__iter__", lambda self: iter([other, target]))

    # Act / Assert
    assert media_parts._find_by_sha1("target") is target
    assert media_parts._find_by_sha1("missing") is None
