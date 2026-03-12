from typing import Any

from formulaic.core import Structure


class Schematiser:
    def struct_to_representation(self, struct: Structure, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def representation_to_string(self, representation, *args, **kwargs) -> str:
        raise NotImplementedError()

    def struct_to_string(self, struct: Structure, *args, **kwargs) -> str:
        repr = self.struct_to_representation(struct, *args, **kwargs)
        return self.representation_to_string(repr, *args, **kwargs)
