from typing import Union

from formulaic.core import Structure
from formulaic.objects import FormulaicObject, FormulaicMixin


class Serialiser:
    def __init__(self, *args, **kwargs):
        pass

    def to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")

    def to_string(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct: Structure=None, **kwargs):
        repr = self.to_representation(data, struct, **kwargs)
        return self.serialise(repr, **kwargs)

    def serialise(self, representation, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")

    def from_representation(self, representation, struct:Structure, **kwargs) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")

    def from_string(self, string:str, struct:Structure, **kwargs) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")