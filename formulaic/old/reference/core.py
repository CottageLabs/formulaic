class FormulaicObject:
    struct = None

    def __init__(self, data):
        self._data = data

    def set(self, field, value):
        pass

    def get(self, field):
        pass

    @property
    def data(self):
        return self._data

    def validate(self):
        self.struct.validate(self.data)

class Field:
    name = "_field"
    coerce = [
        {"coerce": None, "allow_coerce_failure": False}
    ]
    allowed_values = []
    validators = []

    def validate(self, value, formulaic_object=None):
        vr = ValidationResult()
        for v in self.validators:
            err = v.validate(value, self, formulaic_object)
            if err is not True:
                vr.add_error(err)
        if vr.is_valid():
            return True
        return vr

    @classmethod
    def make(cls, name):
        class OneTimeField(cls):
            name = name
        return OneTimeField

class Structure:
    name = "_structure"
    fields = []
    lists = []
    objects = []
    validators = []

    def get(self, field_path):
        pass

    def _get(self, nested_field_or_struct):
        if nested_field_or_struct in fields:
            return FieldRef(nested_field_or_struct, self)

    def _field_iterator(self):
        for f in self.fields:
            if isinstance(f, dict):
                yield f
            if isinstance(f, tuple):
                yield {"field": f[0], "required": f[1]}
            else:
                yield {"field": f, "required": False}

    def validate(self, formulaic_object):
        vr = ValidationResult()
        for f in self._field_iterator():
            val = formulaic_object.get(f)
            if f["required"] and val is None:
                vr.add_error(ValidationError(f, val, Required))
            else:
                err = f.validate(formulaic_object.get(f), f, formulaic_object)
                if err is not True:
                    return vr.add_error(err)
        # and so on for lists and objects
        if vr.is_valid:
            return True
        return vr

class FieldRef:
    def __init__(self, field_or_struct, parent):
        self.field_or_struct = field_or_struct
        self.parent = parent

    def _get(self, nested_field_or_struct):
        if nested_field_or_struct in self.field_or_struct:
            return FieldRef(nested_field_or_struct, self)


class FormField(Field):
    label = "label"
    control = None
    default = None
    placeholder = None
    disabled = False
    options = None


class Radio:
    def __init__(self, *args, **kwargs):
        pass

    def render(self, name, value, checked=False):
        chfrag = "checked" if checked else ""
        control = f'<input type="radio" name="${name}" value="${value}" ${chfrag}>'
        return control

class Coerce:
    def __init__(self):
        pass

    def coerce(self, val):
        pass

class Unicode(Coerce):
    def coerce(self, val):
        if isinstance(val, str):
            return val
        elif isinstance(val, str):
            try:
                return val.decode("utf8", "strict")
            except UnicodeDecodeError:
                raise ValueError("Could not decode string")
        else:
            return str(val)

class Boolean(Coerce):
    def coerce(self, val):
        pass

class BigEndDate(Coerce):
    def coerce(self, val):
        pass

class Integer(Coerce):
    def coerce(self, val):
        pass

class LowerCase(Coerce):
    def coerce(self, val):
        pass

class ISOLang2LetterLax(Coerce):
    def coerce(self, val):
        pass

class CurrencyCodeLax(Coerce):
    def coerce(self, val):
        pass