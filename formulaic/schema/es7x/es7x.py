import json

from formulaic.core import Structure, Field, FieldCapability
from formulaic.schema.core import Schematiser

#########################################
## Capability class for ES7x mapping generation

class ES7xCapability(FieldCapability):
    keyword_field = False
    keyword_key = "keyword"
    keyword_store = True
    keyword_ignore_above = 256

    es_type = "text"
    format = None
    index = None
    copy_to = None

    def es_mapping(self):
        mapping = {"type": self.es_type}
        if self.format:
            mapping["format"] = self.format
        if self.index is not None:
            mapping["index"] = self.index
        if self.copy_to:
            mapping["copy_to"] = self.copy_to

        if self.keyword_field:
            kw = {
                self.keyword_key: {
                    "type": "keyword",
                    "store": self.keyword_store
                }
            }
            if self.keyword_ignore_above > 0:
                kw[self.keyword_key]["ignore_above"] = self.keyword_ignore_above

            mapping["fields"] = kw

        return mapping

##############################################
## Mapping generator and its config

class ES7xSchemaConfig:
    dynamic_mappings:list[dict] = None
    additional_mappings:dict = None
    index_settings:dict = None

class ES7xMappingGenerator(Schematiser):
    def __init__(self, config: ES7xSchemaConfig):
        self._config = config
        super(ES7xMappingGenerator, self).__init__()

    @property
    def config(self) -> ES7xSchemaConfig:
        return self._config

    def struct_to_representation(self, struct: Structure, *args, **kwargs) -> "ES7xMapping":
        mappings = self._mappings(struct)
        if self.config.dynamic_mappings is not None:
            mappings["dynamic_templates"] = self.config.dynamic_mappings
        if self.config.additional_mappings is not None:
            self._additional_mappings(mappings)
        settings = self.config.index_settings
        result = {struct.name_: {"mappings": mappings, "settings": settings}}
        return ES7xMapping(result)

    def representation_to_string(self, mapping: "ES7xMapping", *args, **kwargs) -> str:
        return mapping.to_string(*args, **kwargs)

    def _mappings(self, struct: Structure):
        properties = {}

        for entry in struct.ref_.all:
            if isinstance(entry, Field):
                cap = entry.get_capability(ES7xCapability)
                if cap is not None:
                    properties[entry.name] = cap.es_mapping()
            elif isinstance(entry, Structure):
                subs = self._mappings(entry)
                if subs is not None:
                    properties[entry.name_] = subs

        if len(properties) == 0:
            return None

        return {"properties": properties}

    def _additional_mappings(self, mappings: dict):
        ams = self.config.additional_mappings
        for k, v in ams.items():
            bits = k.split(".")
            context = mappings
            for bit in bits:
                if "properties" not in context:
                    context["properties"] = {}
                if bit not in context["properties"]:
                    context["properties"][bit] = {}
                context = context["properties"][bit]
            context.update(v)

class ES7xMapping:
    def __init__(self, mapping):
        self._mapping = mapping

    @property
    def mapping(self):
        return self._mapping

    def to_string(self, *args, **kwargs) -> str:
        return json.dumps(self._mapping, *args, **kwargs)
