import json

from formulaic.core import Structure
from formulaic.serialise.core import Serialiser


class JSONSerialiser(Serialiser):
    def serialise(self, data:dict, struct:Structure, **kwargs):
        # FIXME: to do this properly, we could do with first transforming the dictionary
        # into a safe structure, by traversing and converting all non-json-serialisable types
        # into serialisable ones (e.g. dates to strings, sets to lists, etc)
        #
        # we could do this with the struct, and potentially add a "serialise" attribute to the Field
        # and/or guess the serialisation based on other properties
        return json.dumps(data, **kwargs)

    def parse(self, stream, struct:Structure):
        return json.loads(stream)