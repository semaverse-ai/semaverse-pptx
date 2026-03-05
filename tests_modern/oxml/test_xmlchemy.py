from __future__ import annotations

import pytest

from pptx.exc import InvalidXmlError
from pptx.oxml import parse_xml, register_element_cls
from pptx.oxml.ns import nsdecls, qn
from pptx.oxml.simpletypes import BaseIntType
from pptx.oxml.xmlchemy import (
    BaseAttribute,
    BaseOxmlElement,
    Choice,
    OneAndOnlyOne,
    OneOrMore,
    OptionalAttribute,
    RequiredAttribute,
    XmlString,
    ZeroOrMore,
    ZeroOrOne,
    ZeroOrOneChoice,
)


class ST_IntegerType(BaseIntType):
    @classmethod
    def validate(cls, value):
        cls.validate_int(value)
        if value < 1 or value > 42:
            raise ValueError("value must be in range 1 to 42 inclusive")


class CT_Parent(BaseOxmlElement):
    eg_zooChoice = ZeroOrOneChoice(
        (Choice("cp:choice"), Choice("cp:choice2")),
        successors=("cp:oomChild", "cp:oooChild"),
    )
    oomChild = OneOrMore("cp:oomChild", successors=("cp:oooChild", "cp:zomChild", "cp:zooChild"))
    oooChild = OneAndOnlyOne("cp:oooChild")
    zomChild = ZeroOrMore("cp:zomChild", successors=("cp:zooChild",))
    zooChild = ZeroOrOne("cp:zooChild", successors=())
    optAttr = OptionalAttribute("cp:optAttr", ST_IntegerType)
    reqAttr = RequiredAttribute("reqAttr", ST_IntegerType)


class CT_Choice(BaseOxmlElement):
    pass


class CT_Choice2(BaseOxmlElement):
    pass


class CT_OomChild(BaseOxmlElement):
    pass


class CT_OooChild(BaseOxmlElement):
    pass


class CT_ZomChild(BaseOxmlElement):
    pass


class CT_ZooChild(BaseOxmlElement):
    pass


register_element_cls("cp:parent", CT_Parent)
register_element_cls("cp:choice", CT_Choice)
register_element_cls("cp:choice2", CT_Choice2)
register_element_cls("cp:oomChild", CT_OomChild)
register_element_cls("cp:oooChild", CT_OooChild)
register_element_cls("cp:zomChild", CT_ZomChild)
register_element_cls("cp:zooChild", CT_ZooChild)


def parent_elm(xml_body: str = "") -> CT_Parent:
    return parse_xml(f"<cp:parent {nsdecls('cp')}>{xml_body}</cp:parent>")


def test_meta_oxml_element_metaclass():
    metaclass_name = type(CT_Parent).__name__
    assert metaclass_name == "MetaOxmlElement"


def test_xml_string_eq_ignores_attribute_order():
    xml_string = XmlString('<a:x attr_1="1" attr_2="2"/>')
    equivalent_xml = '<a:x attr_2="2" attr_1="1"/>'
    is_equal = xml_string == equivalent_xml
    assert is_equal


def test_xml_string_ne_for_non_string():
    xml_string = XmlString("<a:x/>")
    is_not_equal = xml_string != object()
    assert is_not_equal


def test_xml_string_eq_false_for_non_equivalent_xml():
    xml_string = XmlString("<a:x/>")
    different_xml = "<a:y/>"
    is_equal = xml_string == different_xml
    assert not is_equal


def test_xml_string_raises_on_non_xml_line():
    xml_string = XmlString("<a:x/>")
    with pytest.raises(ValueError):
        xml_string._parse_line("not xml")


@pytest.mark.parametrize(
    "choice_tag",
    ["choice", None],
)
def test_choice_getter(choice_tag):
    xml_body = f"<cp:{choice_tag}/>" if choice_tag else ""
    parent = parent_elm(xml_body)
    choice = parent.choice
    if choice_tag is None:
        assert choice is None
        return
    assert isinstance(choice, CT_Choice)


def test_choice_creator(snapshot):
    parent = parent_elm()
    choice = parent._new_choice()
    assert str(choice.xml) == snapshot


def test_choice_inserter(snapshot):
    parent = parent_elm("<cp:oomChild/><cp:oooChild/>")
    choice = parent._new_choice()
    parent._insert_choice(choice)
    assert str(parent.xml) == snapshot


def test_choice_adder(snapshot):
    parent = parent_elm()
    choice = parent._add_choice()
    assert isinstance(choice, CT_Choice)
    assert str(parent.xml) == snapshot


@pytest.mark.parametrize(
    "choice_tag",
    ["choice2", None, "choice"],
)
def test_choice_get_or_change_to(choice_tag, snapshot):
    xml_body = f"<cp:{choice_tag}/>" if choice_tag else ""
    parent = parent_elm(xml_body)
    choice = parent.get_or_change_to_choice()
    assert isinstance(choice, CT_Choice)
    assert str(parent.xml) == snapshot


def test_ooo_child_getter():
    parent = parent_elm("<cp:oooChild/>")
    ooo_child = parent.oooChild
    assert isinstance(ooo_child, CT_OooChild)


def test_oom_child_getter():
    parent = parent_elm("<cp:oomChild/><cp:oomChild/>")
    oom_children = parent.oomChild_lst
    assert len(oom_children) == 2
    assert isinstance(oom_children[0], CT_OomChild)


def test_oom_child_creator(snapshot):
    parent = parent_elm()
    oom_child = parent._new_oomChild()
    assert str(oom_child.xml) == snapshot


def test_oom_child_inserter(snapshot):
    parent = parent_elm("<cp:oooChild/><cp:zomChild/><cp:zooChild/>")
    oom_child = parent._new_oomChild()
    parent._insert_oomChild(oom_child)
    assert str(parent.xml) == snapshot


def test_oom_child_private_add(snapshot):
    parent = parent_elm()
    oom_child = parent._add_oomChild()
    assert isinstance(oom_child, CT_OomChild)
    assert str(parent.xml) == snapshot


def test_oom_child_public_add(snapshot):
    parent = parent_elm()
    oom_child = parent.add_oomChild()
    assert isinstance(oom_child, CT_OomChild)
    assert str(parent.xml) == snapshot


def test_oom_child_property_removed():
    has_property = hasattr(CT_Parent, "oomChild")
    assert not has_property


def test_optional_attribute_getter():
    parent = parent_elm()
    parent.set(qn("cp:optAttr"), "24")
    opt_attr = parent.optAttr
    assert opt_attr == 24


def test_optional_attribute_getter_returns_default_when_missing():
    parent = parent_elm()
    opt_attr = parent.optAttr
    assert opt_attr is None


@pytest.mark.parametrize(
    "value",
    [36, None],
)
def test_optional_attribute_setter(value, snapshot):
    parent = parent_elm()
    parent.set(qn("cp:optAttr"), "42")
    parent.optAttr = value
    assert str(parent.xml) == snapshot


def test_required_attribute_getter():
    parent = parent_elm()
    parent.set("reqAttr", "42")
    req_attr = parent.reqAttr
    assert req_attr == 42


def test_required_attribute_setter(snapshot):
    parent = parent_elm()
    parent.set("reqAttr", "42")
    parent.reqAttr = 24
    assert str(parent.xml) == snapshot


def test_required_attribute_raises_on_get_when_missing():
    parent = parent_elm()
    with pytest.raises(InvalidXmlError):
        _ = parent.reqAttr


def test_one_and_only_one_raises_on_get_when_missing():
    parent = parent_elm()
    with pytest.raises(InvalidXmlError):
        _ = parent.oooChild


@pytest.mark.parametrize(
    ("value", "expected_exception"),
    [
        (None, TypeError),
        (-4, ValueError),
        ("2", TypeError),
    ],
)
def test_required_attribute_raises_on_invalid_assign(value, expected_exception):
    parent = parent_elm()
    parent.set("reqAttr", "1")
    with pytest.raises(expected_exception):
        parent.reqAttr = value


def test_zom_child_getter():
    parent = parent_elm("<cp:zomChild/><cp:zomChild/>")
    zom_children = parent.zomChild_lst
    assert len(zom_children) == 2
    assert isinstance(zom_children[0], CT_ZomChild)


def test_zom_child_creator(snapshot):
    parent = parent_elm()
    zom_child = parent._new_zomChild()
    assert str(zom_child.xml) == snapshot


def test_zom_child_inserter(snapshot):
    parent = parent_elm("<cp:oomChild/><cp:oooChild/><cp:zooChild/>")
    zom_child = parent._new_zomChild()
    parent._insert_zomChild(zom_child)
    assert str(parent.xml) == snapshot


def test_zom_child_adder(snapshot):
    parent = parent_elm()
    zom_child = parent._add_zomChild()
    assert isinstance(zom_child, CT_ZomChild)
    assert str(parent.xml) == snapshot


def test_zom_child_property_removed():
    has_property = hasattr(CT_Parent, "zomChild")
    assert not has_property


@pytest.mark.parametrize(
    "has_child",
    [True, False],
)
def test_zoo_child_getter(has_child):
    xml_body = "<cp:zooChild/>" if has_child else ""
    parent = parent_elm(xml_body)
    zoo_child = parent.zooChild
    if has_child:
        assert isinstance(zoo_child, CT_ZooChild)
        return
    assert zoo_child is None


def test_zoo_child_adder(snapshot):
    parent = parent_elm()
    zoo_child = parent._add_zooChild()
    assert isinstance(zoo_child, CT_ZooChild)
    assert str(parent.xml) == snapshot


def test_zoo_child_inserter(snapshot):
    parent = parent_elm("<cp:oomChild/><cp:oooChild/><cp:zomChild/>")
    zoo_child = parent._new_zooChild()
    parent._insert_zooChild(zoo_child)
    assert str(parent.xml) == snapshot


@pytest.mark.parametrize(
    "has_child",
    [True, False],
)
def test_zoo_child_get_or_add(has_child, snapshot):
    xml_body = "<cp:zooChild/>" if has_child else ""
    parent = parent_elm(xml_body)
    zoo_child = parent.get_or_add_zooChild()
    assert isinstance(zoo_child, CT_ZooChild)
    assert str(parent.xml) == snapshot


@pytest.mark.parametrize(
    "has_child",
    [True, False],
)
def test_zoo_child_remover(has_child, snapshot):
    xml_body = "<cp:zooChild/>" if has_child else ""
    parent = parent_elm(xml_body)
    parent._remove_zooChild()
    assert str(parent.xml) == snapshot


@pytest.mark.parametrize(
    "choice_tag",
    [None, "choice", "choice2"],
)
def test_zero_or_one_choice_getter(choice_tag):
    xml_body = f"<cp:{choice_tag}/>" if choice_tag else ""
    parent = parent_elm(xml_body)
    choice = parent.eg_zooChoice
    if choice_tag is None:
        assert choice is None
        return

    expected_types = {
        "choice": CT_Choice,
        "choice2": CT_Choice2,
    }
    assert isinstance(choice, expected_types[choice_tag])


def test_base_attribute_getter_not_implemented():
    base_attribute = BaseAttribute("reqAttr", ST_IntegerType)
    with pytest.raises(NotImplementedError):
        _ = base_attribute._getter


def test_base_attribute_setter_not_implemented():
    base_attribute = BaseAttribute("reqAttr", ST_IntegerType)
    with pytest.raises(NotImplementedError):
        _ = base_attribute._setter


def test_choice_property_name_without_namespace_prefix():
    choice = Choice("child")
    prop_name = choice._prop_name
    assert prop_name == "child"


def test_base_oxml_element_repr_includes_tag():
    parent = parent_elm()
    representation = repr(parent)
    assert "CT_Parent" in representation
    assert "<cp:parent>" in representation


def test_base_oxml_element_xpath_uses_standard_nsmap():
    parent = parent_elm()
    nodes = parent.xpath("//cp:parent")
    assert len(nodes) == 1
    assert nodes[0] is parent


def test_base_oxml_element_nsptag_property():
    parent = parent_elm()
    nsptag = parent._nsptag
    assert nsptag == "cp:parent"


def test_optional_attribute_docstring():
    docstring = CT_Parent.optAttr.__doc__
    assert docstring.startswith("ST_IntegerType type-converted value of ")


def test_required_attribute_docstring():
    docstring = CT_Parent.reqAttr.__doc__
    assert docstring.startswith("ST_IntegerType type-converted value of ")


def test_choice_inserter_docstring():
    docstring = CT_Parent._insert_choice.__doc__
    assert docstring.startswith("Return the passed ``<cp:choice>`` ")


def test_choice_adder_docstring():
    docstring = CT_Parent._add_choice.__doc__
    assert docstring.startswith("Add a new ``<cp:choice>`` child element ")


def test_oom_child_inserter_docstring():
    docstring = CT_Parent._insert_oomChild.__doc__
    assert docstring.startswith("Return the passed ``<cp:oomChild>`` ")


def test_oom_child_private_add_docstring():
    docstring = CT_Parent._add_oomChild.__doc__
    assert docstring.startswith("Add a new ``<cp:oomChild>`` child element ")


def test_oom_child_public_add_docstring():
    docstring = CT_Parent.add_oomChild.__doc__
    assert docstring.startswith("Add a new ``<cp:oomChild>`` child element ")


def test_zom_child_inserter_docstring():
    docstring = CT_Parent._insert_zomChild.__doc__
    assert docstring.startswith("Return the passed ``<cp:zomChild>`` ")


def test_zom_child_adder_docstring():
    docstring = CT_Parent._add_zomChild.__doc__
    assert docstring.startswith("Add a new ``<cp:zomChild>`` child element ")


def test_zoo_child_adder_docstring():
    docstring = CT_Parent._add_zooChild.__doc__
    assert docstring.startswith("Add a new ``<cp:zooChild>`` child element ")


def test_zoo_child_inserter_docstring():
    docstring = CT_Parent._insert_zooChild.__doc__
    assert docstring.startswith("Return the passed ``<cp:zooChild>`` ")


def test_zoo_child_get_or_add_docstring():
    docstring = CT_Parent.get_or_add_zooChild.__doc__
    assert docstring.startswith("Return the ``<cp:zooChild>`` child element")


def test_zoo_child_remover_docstring():
    docstring = CT_Parent._remove_zooChild.__doc__
    assert docstring.startswith("Remove all `cp:zooChild` child elements.")


def test_choice_get_or_change_to_docstring():
    docstring = CT_Parent.get_or_change_to_choice.__doc__
    assert docstring.startswith("Return the ``<cp:choice>`` child, replacing any")


def test_zero_or_one_choice_getter_docstring():
    docstring = CT_Parent.eg_zooChoice.__doc__
    assert docstring.startswith("Return the child element belonging to this element group")


def test_choice_group_remover_docstring():
    docstring = CT_Parent._remove_eg_zooChoice.__doc__
    assert docstring.startswith("Remove the current choice group child element if present.")
