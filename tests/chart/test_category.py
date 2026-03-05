from __future__ import annotations

# ruff: noqa: E501
from pptx.chart.category import Categories, Category
from pptx.oxml import parse_xml


def test_categories_basics() -> None:
    x_chart = parse_xml(
        b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:ser><c:cat><c:strRef><c:strCache><c:ptCount val='3'/>"
        b"<c:pt idx='0'><c:v>Foo</c:v></c:pt>"
        b"<c:pt idx='2'><c:v>Baz</c:v></c:pt>"
        b"</c:strCache></c:strRef></c:cat></c:ser></c:barChart>"
    )
    categories = Categories(x_chart)

    assert len(categories) == 3
    assert categories.depth == 1
    assert [c.label for c in categories] == ["Foo", "", "Baz"]
    assert categories.flattened_labels == (("Foo",), ("",), ("Baz",))


def test_categories_multi_level() -> None:
    x_chart = parse_xml(
        b'<c:barChart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">'
        b"<c:ser><c:cat><c:multiLvlStrRef><c:multiLvlStrCache><c:ptCount val='4'/>"
        b"<c:lvl>"
        b"<c:pt idx='0'><c:v>SF</c:v></c:pt><c:pt idx='1'><c:v>LA</c:v></c:pt>"
        b"<c:pt idx='2'><c:v>NY</c:v></c:pt><c:pt idx='3'><c:v>Albany</c:v></c:pt>"
        b"</c:lvl>"
        b"<c:lvl><c:pt idx='0'><c:v>CA</c:v></c:pt><c:pt idx='2'><c:v>NY</c:v></c:pt></c:lvl>"
        b"</c:multiLvlStrCache></c:multiLvlStrRef></c:cat></c:ser></c:barChart>"
    )
    categories = Categories(x_chart)

    assert categories.depth == 2
    assert len(categories.levels) == 2
    assert categories.flattened_labels == (
        ("CA", "SF"),
        ("CA", "LA"),
        ("NY", "NY"),
        ("NY", "Albany"),
    )


def test_category_properties() -> None:
    pt = parse_xml(
        b'<c:pt xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" idx="42"><c:v>Bar</c:v></c:pt>'
    )
    category = Category(pt)

    assert isinstance(category, str)
    assert category.idx == 42
    assert category.label == "Bar"
