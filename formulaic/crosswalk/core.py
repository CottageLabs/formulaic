from copy import deepcopy
from typing import Union, Type, Optional, Any

from formulaic import engine
from formulaic.core import Structure
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin


###################################################
## Crosswalks

class Crosswalk:
    source:Structure = None
    target:Structure = None
    target_class:Optional[Type[Union[FormulaicObject, FormulaicMixin]]] = None
    mapping = []
    errors = []

    def transform(self, data:Union[dict, FormulaicObject, FormulaicMixin]):
        mixin, fo, _, data = unity.expand(data)

        default = Copy()
        result = {}

        for run in self.mapping:
            source = run[0]
            target = run[1]
            if isinstance(target, Structure):
                target = target.ref_

            transformer = run[2] if len(run) > 2 else default

            source_value = None
            if source is not None:
                source_value = engine.get_data(source, data)

            target_value = transformer.transform(source, source_value, mixin, fo, data)
            if target_value is None or (isinstance(target_value, list) and len(target_value) == 0):
                continue

            if target.repeatable:
                if isinstance(target_value, list):
                    for v in target_value:
                        engine.add_to_list(target, v, result)
                else:
                    engine.add_to_list(target, target_value, result)
            else:
                engine.set_data(target, target_value, result)

        if self.target_class is None:
            return result
        else:
            return self.target_class(result)

    def map_errors(self, validation_result):
        pass


class CrosswalkRule:
    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        fo:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        raise NotImplementedError()

#####################################################
## Transformer implementations

class Copy(CrosswalkRule):
    """
    A transformer that copies data from source to target without any changes.

    This is the default transformer, which is why it is defined in the core module, not
    the transformers module
    """

    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        fo:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        return deepcopy(value)


class SetValue(CrosswalkRule):
    def __init__(self, value):
        self.value = value

    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        fo:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        return self.value

class BooleanString(CrosswalkRule):
    """
    A transformer that converts boolean values to "Y" or "N" strings.
    """
    def __init__(self, true="y", false="n"):
        self._true = true
        self._false = false

    def transform(self, source:Optional[Structure],
                        value:Optional[Any],
                        mixin:Optional[FormulaicMixin]=None,
                        fo:Optional[FormulaicObject]=None,
                        full_data:Optional[dict]=None):
        if value is True:
            return self._true
        elif value is False:
            return self._false
        else:
            return None