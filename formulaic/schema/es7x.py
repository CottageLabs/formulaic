import json

from formulaic.core import Structure, Field
from formulaic.schema.core import SchemaConfig, Schematiser, Schema

class ES7xSchemaConfig(SchemaConfig):
    dynamic_mappings:list[dict] = None
    additional_mappings:dict = None
    index_settings:dict = None

    # def __init__(self, dynamic_mappings=None, additional_mappings=None, index_settings=None):
    #     super(ES7xSchemaConfig, self).__init__()
    #     self._dynamic_mappings = dynamic_mappings
    #     self._additional_mappings = additional_mappings or {}
    #     self._index_settings = index_settings or {}

    # @property
    # def dynamic_mappings(self):
    #     return self._dynamic_mappings
    #
    # @property
    # def additional_mappings(self):
    #     return self._additional_mappings
    #
    # @property
    # def index_settings(self):
    #     return self._index_settings


class ES7xMappingGenerator(Schematiser):
    def __init__(self, config: ES7xSchemaConfig):
        super(ES7xMappingGenerator, self).__init__(config)

    @property
    def config(self) -> ES7xSchemaConfig:
        return self._config

    def serialise(self, struct: Structure) -> "ES7xMapping":

        mappings = self._mappings(struct)
        if self.config.dynamic_mappings is not None:
            mappings["dynamic_templates"] = self.config.dynamic_mappings
        if self.config.additional_mappings is not None:
            self._additional_mappings(mappings)
        settings = self.config.index_settings
        result = {struct._name: {"mappings": mappings, "settings": settings}}
        return ES7xMapping(result)

    def parse(self, stream):
        pass

    def _mappings(self, struct: Structure):
        properties = {}

        for entry in struct._ref.all:
            if isinstance(entry, ES7xStorableField):
                properties[entry.name] = entry.es_mapping()
            elif isinstance(entry, Structure):
                subs = self._mappings(entry)
                if subs is not None:
                    properties[entry._name] = subs

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

class ES7xMapping(Schema):
    def __init__(self, mapping):
        self._mapping = mapping

    @property
    def mapping(self):
        return self._mapping

    def to_string(self) -> str:
        return json.dumps(self._mapping, indent=2)


class ES7xStorableField(Field):
    es_keyword_field = False
    es_keyword_key = "keyword"
    es_keyword_store = True
    es_keyword_ignore_above = 256

    es_type = "text"
    es_format = None
    es_index = None
    es_copy_to = None

    def es_mapping(self):
        mapping = {"type": self.es_type}
        if self.es_format:
            mapping["format"] = self.es_format
        if self.es_index is not None:
            mapping["index"] = self.es_index
        if self.es_copy_to:
            mapping["copy_to"] = self.es_copy_to

        if self.es_keyword_field:
            kw = {
                self.es_keyword_key: {
                    "type": "keyword",
                    "store": self.es_keyword_store
                }
            }
            if self.es_keyword_ignore_above > 0:
                kw[self.es_keyword_key]["ignore_above"] = self.es_keyword_ignore_above

            mapping["fields"] = kw

        return mapping

