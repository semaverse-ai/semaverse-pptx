from __future__ import annotations

import hashlib

from pptx.media import Video
from pptx.package import Package
from pptx.parts.media import MediaPart


def test_media_part_new() -> None:
    pkg = Package(None)
    blob = b"dummy video bytes"
    video = Video.from_blob(blob, "video/mp4", "dummy.mp4")

    part = MediaPart.new(pkg, video)

    assert isinstance(part, MediaPart)
    assert part.blob == blob
    assert part.content_type == "video/mp4"
    assert part.partname.startswith("/ppt/media/media")


def test_media_part_sha1() -> None:
    part = MediaPart(None, None, None, b"blobish-bytes")

    assert part.sha1 == hashlib.sha1(b"blobish-bytes").hexdigest()
