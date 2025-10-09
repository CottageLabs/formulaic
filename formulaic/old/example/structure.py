OBJECT_STRUCTURE = {
    "fields": {
        "id": {
            "coerce": {
                "pipeline": ["unicode"],
                "allow_coerce_failure": False
            },
            "required": True,
            "validate": [
                "is_uuid"
            ]
        }
    },
    "lists": {
        "keywords": {
            "contains": "field",
            "coerce": "unicode",
            "validate": []
        },
        "subject": {"contains": "object"}
    },
    "objects": ["record"],
    "structs": {
        "record": {
            "fields": {
                "title": {}
            },
            "lists": {
                "authors": {"contains": "field"}
            }
        },
        "subject": {

        }
    }
}


FORM_STRUCTURE = {
    "fields": {
        "id": {
            "coerce": {
                "pipeline": ["unicode"],
                "allow_coerce_failure": False
            },
            "required": True,
            "validate": [
                "is_uuid"
            ]
        },
        "title": {
            "coerce": {
                "pipeline": ["unicode"],
                "allow_coerce_failure": False
            },
            "required": True,
            "validate": []
        }
    },
    "lists": {
        "keywords": {
            "contains": "field",
            "coerce": "unicode",
            "validate": []
        },
        "subject": {"contains": "field", "coerce": "unicode"},
        "authors": {"contains": "field", "coerce": "unicode"}
    }
}

def to_unicode(str):
    return str


class Field:
    name = "_field"
    coerce = {
        "pipeline": [],
        "allow_coerce_failure": False
    }
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

class Structure:
    name = "_structure"
    fields = []
    lists = []
    objects = []
    validators = []

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


class ID(Field):
    name = "id",
    coerce = {
        "pipeline": [to_unicode],
        "allow_coerce_failure": False
    }
    validate = [
        IsUUID
    ]

class Keywords(Field):
    name = "keywords"
    coerce = to_unicode
    validate = []

class Scheme(Field):
    name = "scheme"
    coerce = to_unicode
    validate = []

class Value(Field):
    name = "value"
    coerce = to_unicode
    validate = []

class Subject(Structure):
    name = "subject"
    fields = [
        Scheme,
        Value
    ]


class Title(Field):
    name = "title"
    coerce = {
        "pipeline": ["unicode"],
        "allow_coerce_failure": False
    }
    validate: []

class Authors(Field):
    name = "authors"
    coerce = to_unicode
    validate = []

# Object Structure
class Record(Structure):
    fields = [
        Title
    ]
    lists = [
        Authors
    ]

class Top(Structure):
    fields = [
        {"field": ID, "required": True}
    ]
    lists = [
        Keywords,
        Subject
    ]
    objects = [
        Record
    ]

# Form structure

class FormSubject(Field):
    name = "subject"
    coerce = to_unicode
    validate = []

class Form(Structure):
    fields = [
        ID,
        Title
    ]
    lists = [
        Keywords,
        FormSubject,
        Authors
    ]