from typing import Union

from formulaic.lib import unity

OPTIONAL = "optional"
REQUIRED = "required"

SINGLE = "single"
REPEATABLE = "repeatable"

UNIQUE = "unique"
DUPLICABLE = "duplicable"


class Field:
    name = "_field"

    # There is no coerce-in and coerce-out.  Our objective is to keep data in its correct form.  If you
    # want to convert that data, then you need to do that explicitly externally to this code, or
    # transform to another field which has the appropriate coercion.
    coerce = []
    allow_coerce_failure = False

    allowed_values = []
    allowed_range = ()
    allow_none = True
    ignore_none = False

    validators = []

    _parent = None
    _need = OPTIONAL
    _multiplicity = SINGLE
    _duplicability = DUPLICABLE

    def __init__(self, need=OPTIONAL, multiplicity=SINGLE, duplicability=DUPLICABLE, parent=None):
        self._need = need
        self._multiplicity = multiplicity
        self._duplicability = duplicability
        self._parent = parent

    def set_parent(self, parent):
        self._parent = parent

    @property
    def need(self):
        return self._need

    @property
    def required(self):
        return self._need == REQUIRED

    @property
    def multiplicity(self):
        return self._multiplicity

    @property
    def repeatable(self):
        return self._multiplicity == REPEATABLE

    @property
    def duplicability(self):
        return self._duplicability

    @property
    def unique(self):
        return self._duplicability == UNIQUE

    @property
    def parent(self):
        return self._parent

    @property
    def path(self):
        parts = [self.name]
        if self.parent is not None:
            parent_path = self.parent._ref.path
            parts = parent_path + parts
        return parts

    # def validate(self, value, formulaic_object=None):
    #     vr = ValidationResult()
    #     for v in self.validators:
    #         err = v.validate(value, self, formulaic_object)
    #         if err is not True:
    #             vr.add_error(err)
    #     if vr.is_valid():
    #         return True
    #     return vr
    #
    # @classmethod
    # def make(cls, name):
    #     class OneTimeField(cls):
    #         name = name
    #     return OneTimeField

class Structure:
    _name = "_structure"

    # subclasses should add their fields as class attributes
    #
    # my_field = MyField(REQUIRED, SINGLE)

    def __init__(self, required=OPTIONAL, multiplicity=SINGLE, parent=None):
        # separate the properties out into a reference object to keep this
        # class as clean as possible
        self._ref_obj = StructRef(self, required, multiplicity, parent)

        for attr_name, attr_value in self.__class__.__dict__.items():
            if isinstance(attr_value, Field):
                attr_value.set_parent(self)
            elif isinstance(attr_value, Structure):
                attr_value._ref.set_parent(self)

    @property
    def _ref(self):
        return self._ref_obj

class StructRef:
    def __init__(self, struct: Union[Structure, Structure.__class__],
                 need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None):

        if isinstance(struct, type):
            struct = struct()

        self._struct = struct
        self._need = need
        self._multiplicity = multiplicity
        self._duplicability = duplicability
        self._parent = parent

    def set_parent(self, parent):
        self._parent = parent

    @property
    def struct(self):
        return self._struct

    @property
    def need(self):
        return self._need

    @property
    def required(self):
        return self._need == REQUIRED

    @property
    def multiplicity(self):
        return self._multiplicity

    @property
    def repeatable(self):
        return self._multiplicity == REPEATABLE

    @property
    def duplicability(self):
        return self._duplicability

    @property
    def unique(self):
        return self._duplicability == UNIQUE

    @property
    def parent(self):
        return self._parent

    @property
    def path(self):
        # if there is no container above this, then the path is empty, as this object
        # is the root of the structure
        if self.parent is None or not hasattr(self.parent, '_ref'):
            return []
        parent_path = self.parent._ref.path
        parts = parent_path + [self.struct._name]
        return parts

    @property
    def all_required(self):
        return [f for f in self.struct.__dict__.values() if unity.is_required(f)]

    @property
    def structures(self):
        return [f for f in self.struct.__dict__.values() if isinstance(f, Structure)]

    @property
    def all_names(self):
        return [f for f in self.struct.__dict__.values() if unity.name(f)]

    @property
    def fields(self):
        return [f for f in self.struct.__dict__.values() if isinstance(f, Field)]

class Coerce:
    def __init__(self, *args, **kwargs):
        pass

    def coerce(self, val, field):
        pass

class Validator:
    def __init__(self, *args, **kwargs):
        pass

    def validate(self, val, field):
        pass

class DataError(Exception):
    def __init__(self, field, original_value, code, **kwargs):
        super(Exception, self).__init__(field, original_value, code, kwargs)
        self.field = field
        self.original_value = original_value
        self.code = code
        self.params = kwargs

class ValidationError(DataError):
    def __str__(self):
        s = (f"ValidationError: `{self.code}` "
             f"on field `{self.field.name}` "
             f"at path `{self.field.path}` "
             f"with original value `{self.original_value}`")
        return s

class CoerceError(DataError):
    def __str__(self):
        s = (f"CoerceError: `{self.code}` "
             f"on field `{self.field.name}` "
             f"at path `{self.field.path}` "
             f"with original value `{self.original_value}`")
        return s

class StructureError(DataError):
    def __str__(self):
        s = (f"StructureError: `{self.code}` "
             f"on field `{self.field.name}` "
             f"at path `{self.field.path}` "
             f"with original value `{self.original_value}`")
        return s

class ErrorCode:
    id = "_id"

    def __init__(self, *args, **kwargs):
        pass

class DataProcessingResult(Exception):
    def __init__(self, errors=None):
        super(Exception, self).__init__()
        self.errors = errors if errors is not None else []

    def add_error(self, error):
        self.errors.append(error)

    def is_valid(self):
        return len(self.errors) == 0

    def merge(self, other):
        self.errors.extend(other.errors)
