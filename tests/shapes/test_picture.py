from __future__ import annotations

from pathlib import Path

import pytest

from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE, PP_MEDIA_TYPE
from pptx.oxml import parse_xml
from pptx.shapes.picture import Movie, Picture


def test_base_picture_crops(parent) -> None:
    picture = Picture(
        parse_xml(
            b"""
            <p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                   xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvPicPr>
                <p:cNvPr id="42" name="Pic 1"/>
                <p:cNvPicPr/>
                <p:nvPr/>
              </p:nvPicPr>
              <p:blipFill>
                <a:srcRect l="10000" t="20000" r="30000" b="40000"/>
              </p:blipFill>
              <p:spPr>
                <a:prstGeom prst="rect"/>
              </p:spPr>
            </p:pic>
            """
        ),
        parent,
    )

    assert picture.crop_left == 0.1
    assert picture.crop_top == 0.2
    assert picture.crop_right == 0.3
    assert picture.crop_bottom == 0.4

    picture.crop_left = 0.5
    picture.crop_top = 0.6
    picture.crop_right = 0.7
    picture.crop_bottom = 0.8

    assert picture.crop_left == 0.5
    assert picture.crop_top == 0.6
    assert picture.crop_right == 0.7
    assert picture.crop_bottom == 0.8


def test_picture_shape_type_and_mask(parent) -> None:
    picture = Picture(
        parse_xml(
            b"""
            <p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                   xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvPicPr>
                <p:cNvPr id="42" name="Pic 1"/>
                <p:cNvPicPr/>
                <p:nvPr/>
              </p:nvPicPr>
              <p:blipFill/>
              <p:spPr>
                <a:prstGeom prst="rect"/>
              </p:spPr>
            </p:pic>
            """
        ),
        parent,
    )

    assert picture.shape_type == MSO_SHAPE_TYPE.PICTURE
    assert picture.auto_shape_type == MSO_SHAPE.RECTANGLE

    picture.auto_shape_type = MSO_SHAPE.OVAL

    assert picture.auto_shape_type == MSO_SHAPE.OVAL


def test_picture_line_access(parent) -> None:
    picture = Picture(
        parse_xml(
            b"""
            <p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                   xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvPicPr>
                <p:cNvPr id="42" name="Pic 1"/>
                <p:cNvPicPr/>
                <p:nvPr/>
              </p:nvPicPr>
              <p:blipFill/>
              <p:spPr>
                <a:prstGeom prst="rect"/>
              </p:spPr>
            </p:pic>
            """
        ),
        parent,
    )

    picture.line.width = 12700

    assert picture.line.width == 12700


def test_picture_image(parent, test_files_dir: Path) -> None:
    image_part, r_id = parent.part.get_or_add_image_part(str(test_files_dir / "python-icon.jpeg"))
    picture_xml = (
        b'<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        b'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        b'<p:nvPicPr><p:cNvPr id="42" name="Pic 1"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
        b'<p:blipFill><a:blip r:embed="%b"/></p:blipFill>'
        b'<p:spPr><a:prstGeom prst="rect"/></p:spPr>'
        b"</p:pic>"
    ) % r_id.encode("utf-8")

    picture = Picture(
        parse_xml(picture_xml),
        parent,
    )

    assert picture.image.sha1 == image_part.image.sha1


def test_picture_image_raises_when_missing(parent) -> None:
    picture = Picture(
        parse_xml(
            b"""
            <p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                   xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <p:nvPicPr>
                <p:cNvPr id="42" name="Pic 1"/>
                <p:cNvPicPr/>
                <p:nvPr/>
              </p:nvPicPr>
              <p:blipFill><a:blip/></p:blipFill>
              <p:spPr>
                <a:prstGeom prst="rect"/>
              </p:spPr>
            </p:pic>
            """
        ),
        parent,
    )

    with pytest.raises(ValueError, match="no embedded image"):
        _ = picture.image


def test_movie_properties(parent, test_files_dir: Path) -> None:
    _, poster_rid = parent.part.get_or_add_image_part(str(test_files_dir / "python-icon.jpeg"))
    movie_xml = (
        b'<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        b'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        b'<p:nvPicPr><p:cNvPr id="42" name="Movie"/><p:cNvPicPr/>'
        b'<p:nvPr><a:videoFile r:link="rIdVideo"/></p:nvPr></p:nvPicPr>'
        b'<p:blipFill><a:blip r:embed="%b"/></p:blipFill>'
        b"<p:spPr/>"
        b"</p:pic>"
    ) % poster_rid.encode("utf-8")

    movie = Movie(
        parse_xml(movie_xml),
        parent,
    )

    assert movie.shape_type == MSO_SHAPE_TYPE.MEDIA
    assert movie.media_type == PP_MEDIA_TYPE.MOVIE
    assert movie.media_format is not None
    assert movie.poster_frame is not None
