from __future__ import annotations

import hashlib
from pathlib import Path

from pptx.package import Package
from pptx.parts.image import Image, ImagePart
from pptx.util import Emu


def test_image_part_new(test_files_dir: Path) -> None:
    pkg = Package(None)
    blob = (test_files_dir / "python-icon.jpeg").read_bytes()

    image = Image.from_blob(blob)
    part = ImagePart.new(pkg, image)

    assert isinstance(part, ImagePart)
    assert part.blob == blob
    assert part.content_type == "image/jpeg"
    assert part.partname.startswith("/ppt/media/image")


def test_image_part_scale_native_size(test_files_dir: Path) -> None:
    blob = (test_files_dir / "python-icon.jpeg").read_bytes()
    part = ImagePart(None, None, None, blob)

    width, height = part.scale(None, None)

    assert (width, height) == (Emu(2590800), Emu(2590800))


def test_image_part_scale_fixed_width(test_files_dir: Path) -> None:
    blob = (test_files_dir / "python-icon.jpeg").read_bytes()
    part = ImagePart(None, None, None, blob)

    assert part.scale(1000, None) == (1000, 1000)


def test_image_part_scale_fixed_height(test_files_dir: Path) -> None:
    blob = (test_files_dir / "python-icon.jpeg").read_bytes()
    part = ImagePart(None, None, None, blob)

    assert part.scale(None, 3000) == (3000, 3000)


def test_image_part_scale_explicit_dimensions(test_files_dir: Path) -> None:
    blob = (test_files_dir / "python-icon.jpeg").read_bytes()
    part = ImagePart(None, None, None, blob)

    assert part.scale(3337, 9999) == (3337, 9999)


def test_image_properties(test_files_dir: Path) -> None:
    blob = (test_files_dir / "python-icon.jpeg").read_bytes()

    image = Image.from_blob(blob, "python-icon.jpeg")

    assert image.blob == blob
    assert image.content_type == "image/jpeg"
    assert image.ext == "jpg"
    assert image.dpi == (72, 72)
    assert image.filename == "python-icon.jpeg"
    assert image.size == (204, 204)
    assert image.sha1 == hashlib.sha1(blob).hexdigest()


def test_image_from_file_path(test_files_dir: Path) -> None:
    image = Image.from_file(str(test_files_dir / "python-icon.jpeg"))

    assert image.ext == "jpg"


def test_image_from_file_stream(test_files_dir: Path) -> None:
    with (test_files_dir / "python-icon.jpeg").open("rb") as f:
        image = Image.from_file(f)

    assert image.ext == "jpg"
