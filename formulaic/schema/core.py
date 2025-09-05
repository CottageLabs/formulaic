from formulaic.core import Structure

class SchemaConfig:
    pass

class Schematiser:
    def __init__(self, config: SchemaConfig):
        self._config = config

    @property
    def config(self) -> SchemaConfig:
        return self._config

    def serialise(self, struct: Structure) -> "Schema":
        raise NotImplementedError()

    def parse(self, stream):
        raise NotImplementedError()

class Schema:
    def to_string(self) -> str:
        raise NotImplementedError()
