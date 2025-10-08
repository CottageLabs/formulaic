from formulaic.core import Structure


class Serialiser:
    def serialise(self, data:dict, struct:Structure):
        raise NotImplementedError("Subclasses must implement this method.")

    def parse(self, stream, struct:Structure):
        raise NotImplementedError("Subclasses must implement this method.")