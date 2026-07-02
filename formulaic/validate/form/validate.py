from typing import Union, Literal

from formulaic.core import Validator, ValidationError
from formulaic.error_codes import DisallowedValue
from formulaic.serialise.form.core import FormFieldCapability


class LimitToFormOptions(Validator):
    def validate(self, val, data, value_context):
        if val is None:
            return True

        cap = self._reference.get_capability(FormFieldCapability)
        if cap is None:
            return True

        allowed = [o.get("value") for o in cap.options]

        if isinstance(val, list):
            for v in val:
                if v not in allowed:
                    return ValidationError(self._reference, val, DisallowedValue(self, v))
        else:
            if val not in allowed:
                return ValidationError(self._reference, val, DisallowedValue(self, val))

        return True