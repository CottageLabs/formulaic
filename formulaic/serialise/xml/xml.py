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
## Extension objects for Fields and Structuresto support XML-specific metadata

class XMLFieldCapability(FieldCapability):
    """
    Capability class for XML serialisation of fields.

    Add this class to your Field's capability list like

    ```
    class MyField(Field):
        capabilities = (XMLFieldCapability(),)
    ```
    """
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
    """
    Capability class for XML serialisation of structures.

    Add this class to your Structure's capability list like

    ```
    class MyStruct(Structure):
        capabilities_ = (XMLStructureCapability(),)
    ```
    """
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
    """
    Serialiser for XML format. Converts formulaic data to an XML ElementTree Element, which can then be serialised to a string.

    Fields must either have an XMLFieldCapability subclass in their capabilities, or be able to use the default Capability provided
    by XMLFieldCapability. Structures must either have an XMLStructureCapability subclass in their capabilities, or be able to use the default
    Capability provided by XMLStructureCapability.
    """
    def __init__(self,
                 field_capability_class=None,
                 structure_capability_class=None,
                 field_capability_default=None,
                 struct_capability_default=None
                 ):
        """
        Construct an XMLSerialiser.  You may provide custom capability classes and default classes for Fields and Structures.

        :param field_capability_class: The class to use as the base class for all Field Capabilities. Must be a subclass of XMLFieldCapability. If not provided, XMLFieldCapability will be used.
        :param structure_capability_class: The class to use as the base class for all Structure Capabilities. Must be a subclass of XMLStructureCapability. If not provided, XMLStructureCapability will be used.
        :param field_capability_default: An instance of an XMLFieldCapability subclass to use as the default capability for Fields that do not have a specific capability. If not provided, an instance of XMLFieldCapability will be used.
        :param struct_capability_default: An instance of an XMLStructureCapability subclass to use as the default capability for Structures that do not have a specific capability. If not provided, an instance of XMLStructureCapability will be used.
        """

        self._field_capability_class = field_capability_class or XMLFieldCapability
        self._structure_capability_class = structure_capability_class or XMLStructureCapability
        self._field_capability_default = field_capability_default or XMLFieldCapability()
        self._struct_capability_default = struct_capability_default or XMLStructureCapability()
        super().__init__()

    def get_capability(self, reference:Union[Field, Structure, StructRef]) -> Union[XMLFieldCapability, XMLStructureCapability]:
        """
        Obtain the XMLFieldCapability or XMLStructureCapability for a given Field, Structure, or StructRef. If the
        reference does not have a specific capability, the default capability will be returned based on whether the reference is a Field or a Structure.

        :param reference:
        :return:
        """
        cap = unity.get_capability(reference, (self._field_capability_class, self._structure_capability_class))
        if cap is None:
            if isinstance(reference, Field):
                cap = self._field_capability_default
            elif isinstance(reference, (Structure, StructRef)):
                cap = self._struct_capability_default
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

    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        """
        Convert the data from the internal formulaic format to an XML ElementTree Element.

        :param data:
        :param struct:
        :param kwargs:
        :return:
        """
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

    def representation_to_string(self, representation, pretty:bool=False, xml_declaration:bool=True, **kwargs):
        """
        Convert the intermediate representation (an XML ElementTree Element) to a string. By default, the
        output will include an XML declaration and will not be pretty-printed. You can change this with the
        pretty and xml_declaration parameters.

        :param representation:
        :param pretty:
        :param xml_declaration:
        :param kwargs:
        :return:
        """
        xml_str = ET.tostring(representation, encoding="unicode", xml_declaration=xml_declaration)
        if pretty:
            xml_str = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
        return xml_str
