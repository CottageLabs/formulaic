import xml.etree.ElementTree as ET
import xml.dom.minidom

from typing import Union

from formulaic.core import Field, Structure, StructRef, OPTIONAL, SINGLE, DUPLICABLE, FieldCapability, \
    StructureCapability
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser

ELEMENT = "element"
ATTRIBUTE = "attribute"
TEXT = "text"

XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSI = "{%s}" % XSI_NAMESPACE

###################################################
## Extension objects for Fields and StructRefs to support XML-specific metadata

class XMLFieldCapability(FieldCapability):
    namespace = None
    namespace_prefix = None
    entity_type = ELEMENT

    def is_attribute(self):
        return self.entity_type == ATTRIBUTE

    def is_element(self):
        return self.entity_type == ELEMENT

    def is_text(self):
        return self.entity_type == TEXT

class XMLStructureCapability(StructureCapability):
    namespace = None
    namespace_prefix = None
    schema_location = None

    def is_attribute(self):
        return False

    def is_element(self):
        return True

    def is_text(self):
        return False


##################################################
## The XML Serialiser

class XMLSerialiser(Serialiser):
    def __init__(self,
                 field_capability_class=None,
                 structure_capability_class=None,
                 field_capability_default=None,
                 struct_capability_default=None
                 ):
        self._field_capability_class = field_capability_class or XMLFieldCapability
        self._structure_capability_class = structure_capability_class or XMLStructureCapability
        self._field_capability_default = field_capability_default or XMLFieldCapability
        self._struct_capability_default = struct_capability_default or XMLStructureCapability
        super().__init__()

    def get_capability(self, reference:Union[Field, Structure, StructRef]) -> Union[XMLFieldCapability, XMLStructureCapability]:
        cap = unity.get_capability(reference, (self._field_capability_class, self._structure_capability_class))
        if cap is None:
            pass
        return cap

    def _namespace(self, reference:Union[Field, Structure]):
        if isinstance(reference, Structure):
            reference = reference.ref_
        cfg = self.get_capability(reference)

        ident = cfg.namespace
        name = cfg.namespace_prefix

        if name is None:
            name = ""

        prefix = "{" + ident + "}" if ident is not None else ""

        return name, ident, prefix

    def _add_value(self, parent, entry, value, ns_name, ns_ident, ns_prefix):
        if isinstance(entry, Structure):
            entry = entry.ref_

        cfg = self.get_capability(entry)

        ET.register_namespace(ns_name, ns_ident)
        if entry.repeatable:
            for item in value:
                if cfg.is_attribute():
                    parent.set(ns_prefix + entry.name, str(item))
                elif cfg.is_text():
                    parent.text = str(item)
                else:
                    el = ET.SubElement(parent, ns_prefix + entry.name)
                    el.text = str(item)
        else:
            if cfg.is_attribute():
                parent.set(ns_prefix + entry.name, str(value))
            elif cfg.is_text():
                parent.text = str(value)
            else:
                el = ET.SubElement(parent, ns_prefix + entry.name)
                el.text = str(value)

    def to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)

        name, ns, prefix = self._namespace(struct)
        ET.register_namespace(name, ns)

        attrib = {}
        cfg = self.get_capability(struct)
        sl = cfg.schema_location
        if sl is not None:
            attrib[XSI + "schemaLocation"] = sl
            ET.register_namespace("xsi", XSI_NAMESPACE)

        root = ET.Element(prefix + struct.name_, attrib=attrib)

        def recurse(data:dict, struct:Structure, parent):
            for entry in struct.ref_.all:
                if isinstance(entry, Field):
                    name, ns, prefix = self._namespace(entry)
                    value = data.get(entry.name)
                    if value is not None:
                        self._add_value(parent, entry, value, name, ns, prefix)

                elif isinstance(entry, Structure):
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