from __future__ import annotations

import pytest

from pptx.action import ActionSetting, Hyperlink
from pptx.enum.action import PP_ACTION
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml import parse_xml
from tests.stubs import (
    ActionPartStub,
    ParentProxy,
    RelatedSlidePartStub,
    SlideTargetStub,
)


def _c_nvpr(children: bytes = b"") -> object:
    return parse_xml(
        b'<p:cNvPr xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        b'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        b'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        b'id="1" name="Shape 1">' + children + b"</p:cNvPr>"
    )


@pytest.mark.parametrize(
    ("children", "expected_action"),
    [
        (b"", PP_ACTION.NONE),
        (b"<a:hlinkClick/>", PP_ACTION.HYPERLINK),
        (
            b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=firstslide"/>',
            PP_ACTION.FIRST_SLIDE,
        ),
        (
            b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=lastslide"/>',
            PP_ACTION.LAST_SLIDE,
        ),
        (
            b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=nextslide"/>',
            PP_ACTION.NEXT_SLIDE,
        ),
        (
            b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=previousslide"/>',
            PP_ACTION.PREVIOUS_SLIDE,
        ),
        (
            b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=lastslideviewed"/>',
            PP_ACTION.LAST_SLIDE_VIEWED,
        ),
        (
            b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=endshow"/>',
            PP_ACTION.END_SHOW,
        ),
        (b'<a:hlinkClick action="ppaction://hlinksldjump"/>', PP_ACTION.NAMED_SLIDE),
        (b'<a:hlinkClick action="ppaction://hlinkfile"/>', PP_ACTION.OPEN_FILE),
        (b'<a:hlinkClick action="ppaction://hlinkpres"/>', PP_ACTION.PLAY),
        (b'<a:hlinkClick action="ppaction://customshow"/>', PP_ACTION.NAMED_SLIDE_SHOW),
        (b'<a:hlinkClick action="ppaction://ole"/>', PP_ACTION.OLE_VERB),
        (b'<a:hlinkClick action="ppaction://macro"/>', PP_ACTION.RUN_MACRO),
        (b'<a:hlinkClick action="ppaction://program"/>', PP_ACTION.RUN_PROGRAM),
        (b'<a:hlinkClick action="ppaction://media"/>', PP_ACTION.NONE),
    ],
)
def test_action_setting_action_matrix(children: bytes, expected_action: PP_ACTION) -> None:
    action_setting = ActionSetting(_c_nvpr(children), ParentProxy(part=ActionPartStub()))

    action = action_setting.action

    assert action is expected_action


def test_action_setting_hyperlink_property_returns_cached_hyperlink() -> None:
    action_setting = ActionSetting(_c_nvpr(), ParentProxy(part=ActionPartStub()))

    hyperlink_1 = action_setting.hyperlink
    hyperlink_2 = action_setting.hyperlink

    assert isinstance(hyperlink_1, Hyperlink)
    assert hyperlink_2 is hyperlink_1


def test_action_setting_hlink_uses_hover_element_when_hover_true() -> None:
    element = _c_nvpr(
        b'<a:hlinkClick action="ppaction://macro"/><a:hlinkHover action="ppaction://hlinkfile"/>'
    )
    action_setting = ActionSetting(element, ParentProxy(part=ActionPartStub()), hover=True)

    action = action_setting.action

    assert action_setting._hlink is element.hlinkHover
    assert action is PP_ACTION.OPEN_FILE


def test_action_setting_target_slide_returns_none_for_non_slide_jump_action() -> None:
    action_setting = ActionSetting(
        _c_nvpr(b'<a:hlinkClick action="ppaction://macro"/>'),
        ParentProxy(part=ActionPartStub()),
    )

    # Act / Assert
    assert action_setting.target_slide is None


@pytest.mark.parametrize(
    ("children", "expected_index"),
    [
        (b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=firstslide"/>', 0),
        (b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=lastslide"/>', -1),
    ],
)
def test_action_setting_target_slide_returns_first_or_last(
    children: bytes, expected_index: int
) -> None:
    slides = [object(), object(), object()]
    action_setting = ActionSetting(
        _c_nvpr(children),
        ParentProxy(part=ActionPartStub(slide=slides[1], slides=slides)),
    )

    target_slide = action_setting.target_slide

    assert target_slide is slides[expected_index]


@pytest.mark.parametrize(
    ("children", "current_index", "expected_index"),
    [
        (b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=nextslide"/>', 1, 2),
        (b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=previousslide"/>', 1, 0),
    ],
)
def test_action_setting_target_slide_returns_next_or_previous(
    children: bytes, current_index: int, expected_index: int
) -> None:
    slides = [object(), object(), object()]
    action_setting = ActionSetting(
        _c_nvpr(children),
        ParentProxy(part=ActionPartStub(slide=slides[current_index], slides=slides)),
    )

    target_slide = action_setting.target_slide

    assert target_slide is slides[expected_index]


@pytest.mark.parametrize(
    ("children", "current_index", "error_message"),
    [
        (b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=nextslide"/>', 2, "no next slide"),
        (
            b'<a:hlinkClick action="ppaction://hlinkshowjump?jump=previousslide"/>',
            0,
            "no previous slide",
        ),
    ],
)
def test_action_setting_target_slide_raises_at_slide_collection_boundaries(
    children: bytes, current_index: int, error_message: str
) -> None:
    slides = [object(), object(), object()]
    action_setting = ActionSetting(
        _c_nvpr(children),
        ParentProxy(part=ActionPartStub(slide=slides[current_index], slides=slides)),
    )

    # Act / Assert
    with pytest.raises(ValueError, match=error_message):
        _ = action_setting.target_slide


def test_action_setting_target_slide_resolves_named_slide() -> None:
    target_slide = object()
    part = ActionPartStub(related_parts_by_rid={"rId42": RelatedSlidePartStub(slide=target_slide)})
    action_setting = ActionSetting(
        _c_nvpr(b'<a:hlinkClick action="ppaction://hlinksldjump" r:id="rId42"/>'),
        ParentProxy(part=part),
    )

    resolved = action_setting.target_slide

    assert resolved is target_slide


def test_action_setting_target_slide_setter_assigns_named_slide() -> None:
    part = ActionPartStub(relate_to_rid="rId42")
    action_setting = ActionSetting(
        _c_nvpr(b'<a:hlinkClick action="ppaction://macro" r:id="rId9"/>'),
        ParentProxy(part=part),
    )
    target_slide = SlideTargetStub(part="target-slide-part")

    action_setting.target_slide = target_slide

    assert part.dropped_rids == ["rId9"]
    assert part.relate_to_calls == [("target-slide-part", RT.SLIDE, False)]
    assert action_setting._element.hlinkClick is not None
    assert action_setting._element.hlinkClick.action == "ppaction://hlinksldjump"
    assert action_setting._element.hlinkClick.rId == "rId42"


def test_action_setting_target_slide_setter_clears_action_on_none() -> None:
    part = ActionPartStub()
    action_setting = ActionSetting(
        _c_nvpr(b'<a:hlinkClick action="ppaction://macro" r:id="rId9"/>'),
        ParentProxy(part=part),
    )

    action_setting.target_slide = None

    assert part.dropped_rids == ["rId9"]
    assert action_setting._element.hlinkClick is None


@pytest.mark.parametrize(
    ("children", "expected_dropped_rids"),
    [
        (b"", []),
        (b"<a:hlinkClick/>", []),
        (b'<a:hlinkClick r:id="rId8"/>', ["rId8"]),
    ],
)
def test_action_setting_clear_click_action(
    children: bytes, expected_dropped_rids: list[str]
) -> None:
    part = ActionPartStub()
    action_setting = ActionSetting(_c_nvpr(children), ParentProxy(part=part))

    action_setting._clear_click_action()

    assert part.dropped_rids == expected_dropped_rids
    assert action_setting._element.hlinkClick is None


@pytest.mark.parametrize(
    ("children", "target_refs", "expected"),
    [
        (b"", {}, None),
        (b"<a:hlinkClick/>", {}, None),
        (b'<a:hlinkClick r:id="rId1"/>', {"rId1": "https://example.com"}, "https://example.com"),
    ],
)
def test_hyperlink_address_getter(
    children: bytes, target_refs: dict[str, str], expected: str | None
) -> None:
    hyperlink = Hyperlink(
        _c_nvpr(children),
        ParentProxy(part=ActionPartStub(target_refs_by_rid=target_refs)),
    )

    address = hyperlink.address

    assert address == expected


def test_hyperlink_address_setter_adds_click_hyperlink() -> None:
    part = ActionPartStub(relate_to_rid="rId3")
    hyperlink = Hyperlink(_c_nvpr(), ParentProxy(part=part))

    hyperlink.address = "https://example.com"

    assert part.relate_to_calls == [("https://example.com", RT.HYPERLINK, True)]
    assert hyperlink._element.hlinkClick is not None
    assert hyperlink._element.hlinkClick.rId == "rId3"


def test_hyperlink_address_setter_adds_hover_hyperlink_when_hover_true() -> None:
    part = ActionPartStub(relate_to_rid="rId3")
    hyperlink = Hyperlink(_c_nvpr(), ParentProxy(part=part), hover=True)

    hyperlink.address = "https://example.com"

    assert part.relate_to_calls == [("https://example.com", RT.HYPERLINK, True)]
    assert hyperlink._element.hlinkHover is not None
    assert hyperlink._element.hlinkHover.rId == "rId3"


def test_hyperlink_address_setter_replaces_existing_hyperlink() -> None:
    part = ActionPartStub(relate_to_rid="rId3")
    hyperlink = Hyperlink(
        _c_nvpr(b'<a:hlinkClick r:id="rId6"/>'),
        ParentProxy(part=part),
    )

    hyperlink.address = "https://example.com/new"

    assert part.dropped_rids == ["rId6"]
    assert part.relate_to_calls == [("https://example.com/new", RT.HYPERLINK, True)]
    assert hyperlink._element.hlinkClick is not None
    assert hyperlink._element.hlinkClick.rId == "rId3"


@pytest.mark.parametrize(
    ("children", "hover"),
    [
        (b'<a:hlinkClick r:id="rId6"/>', False),
        (b'<a:hlinkHover r:id="rId6"/>', True),
    ],
)
def test_hyperlink_address_setter_removes_hyperlink_when_none(
    children: bytes, hover: bool
) -> None:
    part = ActionPartStub()
    hyperlink = Hyperlink(_c_nvpr(children), ParentProxy(part=part), hover=hover)

    hyperlink.address = None

    assert part.dropped_rids == ["rId6"]
    if hover:
        assert hyperlink._element.hlinkHover is None
    else:
        assert hyperlink._element.hlinkClick is None
