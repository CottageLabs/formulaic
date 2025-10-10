from formulaic import engine
from formulaic.core import Field, Structure, StructRef

from typing import Union

class FormulaicObject:
    struct = None
    silent_prune = False
    allow_other_fields = False
    apply_structure_on_init = True
    check_required_on_init = True
    check_required_on_set = True
    by_reference = True

    def __init__(self, data=None):
        data = data if data is not None else {}
        if self.apply_structure_on_init:
            data = engine.apply_structure(self.struct, data,
                                          required_check=self.check_required_on_init,
                                          silent_prune=self.silent_prune,
                                          allow_other_fields=self.allow_other_fields)
        elif self.check_required_on_init:
            engine.check_required(self.struct, data)

        self._data = data

    @property
    def data(self):
        return self._data

    def get(self, reference: Union[Field, Structure, StructRef], default=None, by_reference:bool=None, coerce=None):
        if by_reference is None:
            by_reference = self.by_reference
        val = engine.get_data(reference, self._data, default=default, by_reference=by_reference)
        if coerce is not None:
            val = coerce.coerce(val, reference)
        return val

    def set(self, reference: Union[Field, Structure, StructRef], value, required_check:bool=None, silent_prune:bool=None, allow_other_fields:bool=None):
        if required_check is None:
            required_check = self.check_required_on_set
        if silent_prune is None:
            silent_prune = self.silent_prune
        if allow_other_fields is None:
            allow_other_fields = self.allow_other_fields
        return engine.set_data(reference, value, self._data,
                               required_check=required_check,
                               silent_prune=silent_prune,
                               allow_other_fields=allow_other_fields)

    def delete(self, reference: Union[Field, Structure, StructRef], prune:bool=None):
        if prune is None:
            prune = self.silent_prune
        return engine.delete_data(reference, self._data, prune=prune)

    def delete_from_list(self, reference: Union[Field, Structure, StructRef], val=None, matchsub=None, prune:bool=None, apply_structure_on_matchsub:bool=True):
        if prune is None:
            prune = self.silent_prune
        return engine.delete_from_list(reference, self._data, val=val, matchsub=matchsub,
                                       prune=prune, apply_structure_on_matchsub=apply_structure_on_matchsub)

    def add_to_list(self, reference: Union[Field, Structure, StructRef], value, required_check:bool=None, silent_prune:bool=None, allow_other_fields:bool=None):
        if required_check is None:
            required_check = self.check_required_on_set
        if silent_prune is None:
            silent_prune = self.silent_prune
        if allow_other_fields is None:
            allow_other_fields = self.allow_other_fields
        return engine.add_to_list(reference, value, self._data,
                                  required_check=required_check,
                                  silent_prune=silent_prune,
                                  allow_other_fields=allow_other_fields)

class FormulaicMixin:
    @property
    def fo(self) -> FormulaicObject:
        return self._data
        # raise NotImplementedError("Subclasses must implement the 'fo' property returning a FormulaicObject instance.")

    @fo.setter
    def fo(self, value: FormulaicObject):
        if not isinstance(value, FormulaicObject):
            raise ValueError("Value must be an instance of FormulaicObject.")
        self._data = value