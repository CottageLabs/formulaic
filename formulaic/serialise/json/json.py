import json
from typing import Union

from formulaic.core import Structure, Field
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser


class JSONSerialiser(Serialiser):
    def _add_value(self, parent, entry, value):
        if isinstance(entry, Structure):
            entry = entry.ref_

        if entry.repeatable:
            for item in value:
                if entry.serialiser is not None:
                    item = entry.serialiser(item)
                parent[entry.name] = item
        else:
            if entry.serialiser is not None:
                value = entry.serialiser(value)
            parent[entry.name] = value

    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        """
        Converts the data from the internal formulaic format to a JSON-compatible representation, which is
        serialisable as-is to JSON

        :param data:
        :param struct:
        :param kwargs:
        :return:
        """
        mixin, fo, struct, data = unity.expand(data, struct)

        root = {}

        def recurse(data: dict, struct: Structure, parent):
            for entry in struct.ref_.all:
                if isinstance(entry, Field):
                    value = data.get(entry.name)
                    if value is not None:
                        self._add_value(parent, entry, value)

                elif isinstance(entry, Structure):
                    value = data.get(entry.name_)
                    if value is not None:
                        if isinstance(value, list):
                            parent[entry.name_] = []
                            for item in value:
                                sub = {}
                                recurse(item, entry, sub)
                                parent[entry.name_].append(sub)
                        elif isinstance(value, dict):
                            sub = {}
                            recurse(value, entry, sub)
                            parent[entry.name_] = sub

        recurse(data, struct, root)
        return root

    def representation_to_string(self, representation:dict, **kwargs):
        """
            Convert the intermediate representation to a JSON string

        :param representation:
        :param kwargs:
        :return:
        """
        return json.dumps(representation, **kwargs)

    def representation_to_data(self, representation, struct:Structure, **kwargs) -> dict:
        """
        Read the intermediate representation from a JSON-compatible format back to the internal formulaic format.

        :param representation:
        :param struct:
        :param kwargs:
        :return:
        """
        # FIXME: this should probably use the engine to construct the data from the structure, rather than just returning the dict
        return json.loads(representation)

    def string_to_representation(self, string:str, struct:Structure, **kwargs) -> dict:
        """
        Read the JSON string and convert it to the intermediate representation (which in this case is just a dict)

        :param string:
        :param struct:
        :param kwargs:
        :return:
        """
        return json.loads(string)