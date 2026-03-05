from __future__ import annotations

from lxml import etree

from pptx.shared import ElementProxy, ParentedElementProxy, PartElementProxy
from tests.stubs import PartProviderStub


def test_element_proxy_equality() -> None:
    p = etree.Element("p")
    q = etree.Element("p")
    proxy = ElementProxy(p)
    proxy_2 = ElementProxy(p)
    proxy_3 = ElementProxy(q)
    not_a_proxy = "Foobar"

    assert (proxy == proxy_2) is True
    assert (proxy == proxy_3) is False
    assert (proxy == not_a_proxy) is False
    assert (proxy != proxy_2) is False
    assert (proxy != proxy_3) is True
    assert (proxy != not_a_proxy) is True


def test_element_proxy_element_property() -> None:
    element = etree.Element("p")
    proxy = ElementProxy(element)

    assert proxy.element is element


def test_parented_element_proxy_parent_property() -> None:
    parent = PartProviderStub(part=object())
    proxy = ParentedElementProxy(etree.Element("p"), parent)

    assert proxy.parent is parent


def test_parented_element_proxy_part_property() -> None:
    part = object()
    parent = PartProviderStub(part=part)
    proxy = ParentedElementProxy(etree.Element("p"), parent)

    assert proxy.part is part


def test_part_element_proxy_part_property() -> None:
    part = object()
    proxy = PartElementProxy(etree.Element("p"), part)

    assert proxy.part is part
