import xml.etree.ElementTree as ET
import xml.dom.minidom

from typing import Union

from formulaic.core import Field, Structure, StructRef, OPTIONAL, SINGLE, DUPLICABLE
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser
from formulaic.serialise.xml2 import XMLFieldCapability

ELEMENT = "element"
ATTRIBUTE = "attribute"
TEXT = "text"

XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSI = "{%s}" % XSI_NAMESPACE

###################################################
## Extension approach

class XMLFieldExtension(object):
    xml_namespace = None
    xml_namespace_prefix = None
    xml_entity_type = ELEMENT

    def xml_is_attribute(self):
        return self.xml_entity_type == ATTRIBUTE

    def xml_is_element(self):
        return self.xml_entity_type == ELEMENT

    def xml_is_text(self):
        return self.xml_entity_type == TEXT

class XMLStructRefExtension(object):
    xml_namespace = None
    xml_namespace_prefix = None
    xml_schema_location = None

    def xml_is_attribute(self):
        return False

    def xml_is_element(self):
        return True

    def xml_is_text(self):
        return False

###################################################
## Extensions on the Field/Structure/StructRef classes to support XML-specific metadata

class XMLField(Field):
    xml_namespace = None
    xml_namespace_prefix = None
    xml_entity_type = ELEMENT

    def xml_is_attribute(self):
        return self.xml_entity_type == ATTRIBUTE

    def xml_is_element(self):
        return self.xml_entity_type == ELEMENT

    def xml_is_text(self):
        return self.xml_entity_type == TEXT


class XMLStructRef(StructRef):
    xml_namespace = None
    xml_namespace_prefix = None
    xml_schema_location = None

    def __init__(self, struct: Union["Structure", "Structure.__class__"],
                 need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None):

        super(XMLStructRef, self).__init__(struct=struct,
                                            need=need,
                                            multiplicity=multiplicity,
                                            duplicability=duplicability,
                                            parent=parent)

    def xml_is_attribute(self):
        return False

    def xml_is_element(self):
        return True

    def xml_is_text(self):
        return False


class XMLStructure(Structure):
    ref_class_:XMLStructRef = XMLStructRef
    # ref_: XMLStructRef  # For type annotation only

    def __init__(self, need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None):
        super().__init__(need=need,
                         multiplicity=multiplicity,
                         duplicability=duplicability,
                         parent=parent)


##################################################
## The XML Serialiser

class XMLSerialiser(Serialiser):
    def __init__(self, field_capability_class=None, struct_capability_class=None):
        self._field_capability_class = field_capability_class or XMLFieldCapability
        self._struct_capability_class = struct_capability_class or XMLStructureExtension

    def _namespace(self, reference:Union[XMLField, XMLStructure]):
        if isinstance(reference, XMLStructure):
            reference = reference.ref_


        ident = reference.xml_namespace
        name = reference.xml_namespace_prefix

        if name is None:
            name = ""

        prefix = "{" + ident + "}" if ident is not None else ""

        return name, ident, prefix

    def _add_value(self, parent, entry, value, ns_name, ns_ident, ns_prefix):
        if isinstance(entry, XMLStructure):
            entry = entry.ref_

        ET.register_namespace(ns_name, ns_ident)
        if entry.repeatable:
            for item in value:
                if entry.xml_is_attribute():
                    parent.set(ns_prefix + entry.name, str(item))
                elif entry.xml_is_text():
                    parent.text = str(item)
                else:
                    el = ET.SubElement(parent, ns_prefix + entry.name)
                    el.text = str(item)
        else:
            if entry.xml_is_attribute():
                parent.set(ns_prefix + entry.name, str(value))
            elif entry.xml_is_text():
                parent.text = str(value)
            else:
                el = ET.SubElement(parent, ns_prefix + entry.name)
                el.text = str(value)

    def to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:XMLStructure=None, **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)

        name, ns, prefix = self._namespace(struct)
        ET.register_namespace(name, ns)

        attrib = {}
        sl = struct.ref_.xml_schema_location
        if sl is not None:
            attrib[XSI + "schemaLocation"] = sl
            ET.register_namespace("xsi", XSI_NAMESPACE)

        root = ET.Element(prefix + struct.name_, attrib=attrib)

        def recurse(data:dict, struct:XMLStructure, parent):
            for entry in struct.ref_.all:
                if isinstance(entry, XMLField):
                    name, ns, prefix = self._namespace(entry)
                    value = data.get(entry.name)
                    if value is not None:
                        self._add_value(parent, entry, value, name, ns, prefix)

                elif isinstance(entry, XMLStructure):
                    name, ns, prefix = self._namespace(entry)
                    value = data.get(entry.name_)
                    if value is not None:
                        if isinstance(value, list):
                            for item in value:
                                sub_el = ET.SubElement(parent, prefix + entry.name_)
                                recurse(item, entry, sub_el)
                        elif isinstance(value, dict):
                            sub_el = ET.SubElement(parent, prefix + entry.name_)
                            recurse(value, entry, sub_el)

        recurse(data, struct, root)
        return root

    def serialise(self, representation, pretty:bool=False, xml_declaration:bool=True, **kwargs):
        xml_str = ET.tostring(representation, encoding="unicode", xml_declaration=xml_declaration)
        if pretty:
            xml_str = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
        return xml_str

    def parse(self, stream, struct:Structure):
        pass