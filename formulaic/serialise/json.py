import json
from typing import Union

from formulaic.core import Structure, Field
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser


class JSONSerialiser(Serialiser):
    def _add_value(self, parent, entry, value):
        if isinstance(entry, Structure):
            entry = entry._ref

        if entry.repeatable:
            for item in value:
                if entry.serialiser is not None:
                    item = entry.serialiser(item)
                parent[entry.name] = item
        else:
            if entry.serialiser is not None:
                value = entry.serialiser(value)
            parent[entry.name] = value

    def to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)

        root = {}

        def recurse(data: dict, struct: Structure, parent):
            for entry in struct._ref.all:
                if isinstance(entry, Field):
                    value = data.get(entry.name)
                    if value is not None:
                        self._add_value(parent, entry, value)

                elif isinstance(entry, Structure):
                    value = data.get(entry._name)
                    if value is not None:
                        if isinstance(value, list):
                            parent[entry._name] = []
                            for item in value:
                                sub = {}
                                recurse(item, entry, sub)
                                parent[entry._name].append(sub)
                        elif isinstance(value, dict):
                            sub = {}
                            recurse(value, entry, sub)
                            parent[entry._name] = sub

        recurse(data, struct, root)
        return root

    def serialise(self, representation:dict, **kwargs):
        return json.dumps(representation, **kwargs)

    def from_representation(self, representation, struct:Structure, **kwargs) -> dict:
        return json.loads(representation)

    def from_string(self, string:str, struct:Structure, **kwargs) -> dict:
        return json.loads(string)

    def parse(self, stream, struct:Structure):
        return json.loads(stream)