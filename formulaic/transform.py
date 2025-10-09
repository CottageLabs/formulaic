from copy import deepcopy
from typing import Union

from formulaic import engine
from formulaic.objects import FormulaicObject


###################################################
## Transformers/Crosswalks

class Transform:
    source = None
    target = None
    mapping = []
    errors = []

    def transform(self, data:Union[dict, FormulaicObject]):
        if isinstance(data, FormulaicObject):
            data = data.data

        result = {}
        for run in self.mapping:
            source = run[0]
            target = run[1]
            transformer = run[2] if len(run) > 2 else Copy()

            source_value = engine.get_data(source, data)
            target_value = transformer.transform(source_value)
            engine.set_data(target, target_value, result)

        return result

    def map_errors(self, validation_result):
        pass


class Transformer:
    def transform(self, data):
        pass

#####################################################
## Transformer implementations

class Copy(Transformer):
    """
    A transformer that copies data from source to target without any changes.

    This is the default transformer, which is why it is defined in the core module, not
    the transformers module
    """

    def transform(self, data: dict) -> dict:
        return deepcopy(data)

