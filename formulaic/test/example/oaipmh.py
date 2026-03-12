from typing import Union, Optional, Any

from formulaic.core import Field, Structure, SINGLE, OPTIONAL, REPEATABLE, StructRef
from formulaic.fields import BasicUnicode, UTCDateTimeField
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.test.example.models import Journal
from formulaic.test.example.structs import JournalStructure
from formulaic.transform import Transform, Transformer, SetValue
from formulaic.serialise.xml.xml import XMLSerialiser, ATTRIBUTE, TEXT, XMLFieldCapability, XMLStructureCapability, \
    ELEMENT


################################################
## XML Serialisation configuration for DC

# Capability classes

class DCElementXMLFieldCapability(XMLFieldCapability):
    namespace = "http://purl.org/dc/elements/1.1/"
    namespace_prefix = "dc"
    entity_type = ELEMENT

class DCXSIAttributeCapability(XMLFieldCapability):
    entity_type = ATTRIBUTE
    namespace = "http://www.w3.org/2001/XMLSchema-instance"
    namespace_prefix = "xsi"

class DCXMLTextCapability(DCElementXMLFieldCapability):
    entity_type = TEXT

class DCXMLStructureCapability(XMLStructureCapability):
    namespace = "http://purl.org/dc/elements/1.1/"
    namespace_prefix = "dc"
    schema_location = "http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"

# Binding capabilities to all fields and structures
# (Note for the regularly used fields, this could also be done by setting the capability classes as the defaults on
# the serialiser itself)

class DCXMLElementField(Field):
    capabilities = (DCElementXMLFieldCapability(),)

class DCXSIAttributeField(Field):
    capabilities = (DCXSIAttributeCapability(),)

class DCXMLTextField(Field):
    capabilities = (DCXMLTextCapability(),)

class DCXMLStructure(Structure):
    capabilities_ = (DCXMLStructureCapability(),)


##########################################
## DC Fields

# Simple element fields
class DCTitle(BasicUnicode, DCXMLElementField): name = "title"

class DCIdentifier(BasicUnicode, DCXMLElementField): name = "identifier"

class DCDate(UTCDateTimeField, DCXMLElementField): name = "date"

class DCRelation(BasicUnicode, DCXMLElementField): name = "relation"

class DCDescription(BasicUnicode, DCXMLElementField): name = "description"

class DCType(BasicUnicode, DCXMLElementField): name = "type"

class DCCreator(BasicUnicode, DCXMLElementField): name = "creator"

class DCPublisher(BasicUnicode, DCXMLElementField): name = "publisher"

class DCLanguage(BasicUnicode, DCXMLElementField): name = "language"

class DCSource(BasicUnicode, DCXMLElementField): name = "source"

class DCRights(BasicUnicode, DCXMLElementField): name = "rights"

# Subject classification fields and their container structure
class DCSubjectType(BasicUnicode, DCXSIAttributeField): name = "type"

class DCSubjectTerm(BasicUnicode, DCXMLTextField): name = "term"

class DCSubject(DCXMLStructure):
    name_ = "subject"
    type = DCSubjectType(OPTIONAL, SINGLE)
    term = DCSubjectTerm(OPTIONAL, SINGLE)

# The overall Structure
class DublinCoreStructure(DCXMLStructure):
    name_ = "dc"

    title = DCTitle(OPTIONAL, REPEATABLE)
    identifier = DCIdentifier(OPTIONAL, REPEATABLE)
    date = DCDate(OPTIONAL, REPEATABLE)
    relation = DCRelation(OPTIONAL, REPEATABLE)
    description = DCDescription(OPTIONAL, REPEATABLE)
    creator = DCCreator(OPTIONAL, REPEATABLE)
    publisher = DCPublisher(OPTIONAL, REPEATABLE)
    type = DCType(OPTIONAL, REPEATABLE)
    language = DCLanguage(OPTIONAL, REPEATABLE)
    source = DCSource(OPTIONAL, REPEATABLE)
    subject = DCSubject(OPTIONAL, REPEATABLE)
    rights = DCRights(OPTIONAL, REPEATABLE)

#############################################
## Formulaic Object to hold the DC data

class DublinCoreFO(FormulaicObject):
    struct = DublinCoreStructure()

#############################################
## Transformers

class ToCID(Transformer):
    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[Journal]=None,
                        obj:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        if mixin is not None:
            url = f"/toc/{mixin.toc_id}"
            return url
        return None

class SubjectTerm(Transformer):
    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        obj:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        if value is None:
            return None

        result = []
        if not isinstance(value, list):
            value = [value]
        for v in value:
            result.append({"term": v})
        return result

class SubjectSchemeAndTerm(Transformer):
    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        obj:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        if value is None:
            return None

        if not isinstance(value, list):
            value = [value]

        result = []

        for v in value:
            scheme = v.get("scheme")
            code = v.get("code")
            term = v.get("term")

            if scheme and scheme.lower() == 'lcc':
                result.append({
                    "type": "dcterms:LCC",
                    "term": term,
                })
                result.append({
                    "type": "dcterms:LCC",
                    "term": code,
                })
            else:
                if term:
                    result.append({
                        "term": f"{scheme}:{term}",
                    })
                if code:
                    result.append({
                        "term": f"{scheme}:{code}",
                    })

            return result

class RightsTransformer(Transformer):
    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        obj:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        if value is None:
            return None

        if not isinstance(value, list):
            value = [value]

        result = []
        for v in value:
            t = v.get("type")
            if t:
                result.append(t)
        return result

class Journal2DC(Transform):
    source:JournalStructure = JournalStructure()
    target:DublinCoreStructure = DublinCoreStructure()
    target_class:DublinCoreFO = DublinCoreFO

    mapping = [
        (source.bibjson.title, target.title),
        (source.bibjson.pissn, target.identifier),
        (source.bibjson.eissn, target.identifier),
        (None, target.identifier, ToCID()),
        (source.bibjson.language, target.language),
        (source.bibjson.license, target.rights, RightsTransformer()),
        (source.bibjson.publisher.name, target.publisher),
        (source.bibjson.ref.journal, target.relation),
        (source.bibjson.ref.aims_scope, target.relation),
        (source.bibjson.ref.author_instructions, target.relation),
        (source.bibjson.waiver.url, target.relation),
        (source.created_date, target.date),
        (None, target.type, SetValue("journal")),
        (source.bibjson.keywords, target.subject, SubjectTerm()),
        (source.bibjson.subject, target.subject, SubjectSchemeAndTerm()),
    ]

##########################################


from formulaic.test.example.data import JOURNAL_SOURCE
import json

journal = Journal(JOURNAL_SOURCE)
xwalk = Journal2DC()

dc = xwalk.transform(journal)
print(json.dumps(dc.data, indent=4, sort_keys=True))

serialiser = XMLSerialiser()
out = serialiser.data_to_string(dc, DublinCoreStructure(), pretty=True)
print(out)