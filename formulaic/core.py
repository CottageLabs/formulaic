from typing import Union, Callable, Tuple, Any

from formulaic.lib import unity

OPTIONAL = "optional"
REQUIRED = "required"

SINGLE = "single"
REPEATABLE = "repeatable"

UNIQUE = "unique"
DUPLICABLE = "duplicable"


class Field:
    """
    Core field class, providing all essential data-model properties and methods.  Data modellers may subclass this for
    local use, and refinement modules (e.g. forms) may subclass this to provide additional functionality.
    """

    name:str = "_field"
    """Name of the field.  Subclasses should override this to provide a meaningful name."""

    # There is no coerce-in and coerce-out.  Our objective is to keep data in its correct form.  If you
    # want to convert that data, then you need to do that explicitly externally to this code, or
    # transform to another field which has the appropriate coercion.

    coerce:list[Callable] = []
    """List of coercion classes to apply to the field value in order."""

    allow_coerce_failure:bool = False
    """If True, then if coercion fails, the original value will be kept.  If False, then an error will be raised."""

    allowed_values:list[str] = []
    """List of allowed values for the field.  If the value is not in this list, then an error will be raised.  Leave empty to allow any value."""

    allowed_range:Tuple[Any, Any] = ()
    """Tuple of two values representing the allowed range for the field value.  If the value is not in this range, then an error will be raised.  Leave empty to allow any value."""

    allow_none:bool = True
    """If True, then None is allowed as a value for the field.  If False, then an error will be raised if None is set."""

    ignore_none:bool = False
    """If True, then if the value is None, it will be ignored and not set.  If False, then None will be set as the value."""

    validators:list["Validator"] = []
    """List of validator classes to apply to the field value in order.  If any validator fails, an error will be raised."""

    def __init__(self, need:str=OPTIONAL,
                 multiplicity:str=SINGLE,
                 duplicability:str=UNIQUE,
                 parent: "Structure"=None,
                 check_coherence:bool=False):
        """
        Initialize the field with its properties.

        :param need: Is the field required or optional? Use REQUIRED or OPTIONAL.
        :param multiplicity: Is the field single or repeatable? Use SINGLE or REPEATABLE.
        :param duplicability: Is the field unique or duplicable? Use UNIQUE or DUPLICABLE. Applies to repeatable fields only, ignored in other cases.
        :param parent: The containing Structure.  May be left as None, and will be populated when the structure is initialized.
        :param check_coherence: Should the properties of the field be checked for coherence? If True, then the field will check that the properties are coherent with each other.  Useful for testing, not recommended for general usage.
        """
        self._need = need
        self._multiplicity = multiplicity
        self._duplicability = duplicability
        self._parent = parent

        if check_coherence:
            self._check_coherence()

    @property
    def need(self) -> str:
        return self._need

    @property
    def required(self) -> bool:
        return self._need == REQUIRED

    @property
    def optional(self) -> bool:
        return self._need == OPTIONAL

    @property
    def multiplicity(self) -> str:
        return self._multiplicity

    @property
    def repeatable(self) -> bool:
        return self._multiplicity == REPEATABLE

    @property
    def non_repeatable(self) -> bool:
        return self._multiplicity == SINGLE

    @property
    def duplicability(self) -> str:
        return self._duplicability

    @property
    def unique(self) -> bool:
        return self._duplicability == UNIQUE

    @property
    def duplicable(self) -> bool:
        return self._duplicability == DUPLICABLE

    @property
    def parent(self) -> Union[None, "Structure"]:
        return self._parent

    @parent.setter
    def parent(self, parent: "Structure"):
        self._parent = parent

    @property
    def root(self) -> Union["Field", "Structure"]:
        """
        Returns the root structure of the field, which is the parent structure that does not have a parent.
        """
        if self.parent is None:
            return self
        else:
            return self.parent._ref.root

    @property
    def path(self) -> list[str]:
        """
        Returns the path to this field from the root structure as a list of names.
        :return:
        """
        parts = [self.name]
        if self.parent is not None:
            parent_path = self.parent._ref.path
            parts = parent_path + parts
        return parts

    def _check_coherence(self):
        """
        Check the coherence of the field properties.  Raises a ValueError if any incoherence is found.
        :return:
        """
        msg = []
        if self.non_repeatable and self.duplicable:
            msg.append(f"A non-repeatable field cannot be duplicable.")
        if len(self.allowed_range) not in [0, 2]:
            msg.append(f"The allowed_range must be an empty tuple or a tuple of two values.")
        if len(self.allowed_range) == 2:
            lower = self.allowed_range[0]
            upper = self.allowed_range[1]
            if lower > upper:
                msg.append(f"The lower bound of the allowed_range should be less than the upper bound.")
        if self.allowed_values and self.allowed_range:
            msg.append(f"Cannot have both allowed_values and allowed_range set. Choose one or the other.")

        if len(msg) > 0:
            raise ValueError("Coherence check failed for field `{}`: {}".format(self.name, "; ".join(msg)))

    def clone(self):
        """
        Clone the Field, returning a new instance with the same properties.

        Subclasses of Field that add features will need to override this method to ensure the
        clones are suitable
        """
        return self.__class__(need=self.need, multiplicity=self.multiplicity,
                              duplicability=self.duplicability, parent=self.parent)


class StructRef:
    """
    This class sits alongside a Structure and provides all its properties and methods.  This is to keep the Structure
    class as clean as possible, and to separate out the properties of the structure from the structure itself.

    When you want to call functional methods on the Structure, you should do this via this class, which can be
    accessed via the `_ref` property on the Structure.  The methods in this class behave as if they were methods on
    the Structure itself.  It provides you with the same set of methods and properties as you may find on the Field class.
    In addition, it provides interrogative functions, such as listing all fields, structures, required fields, etc.
    """
    def __init__(self, struct: Union["Structure", "Structure.__class__"],
                 need:str=OPTIONAL,
                 multiplicity:str=SINGLE,
                 duplicability:str=DUPLICABLE,
                 parent: "Structure"=None,
                 **kwargs):
        """
        Initialize the structure reference with its properties.  You should not do this directly, instead
        the Structure class will do this for you.

        :param struct:
        :param need:
        :param multiplicity:
        :param duplicability:
        :param parent:
        :param kwargs:
        """

        if isinstance(struct, type):
            struct = struct()

        self._struct = struct
        self._need = need
        self._multiplicity = multiplicity
        self._duplicability = duplicability
        self._parent = parent

    def clone(self):
        """
        Clone the inner Structure, returning a new instance with the same properties.

        Subclasses of StructRef that add features will need to override this method to ensure the
        clones are suitable
        """
        return self.struct.__class__(need=self.need, multiplicity=self.multiplicity,
                         duplicability=self.duplicability, parent=self.parent)

    @property
    def name(self) -> str:
        return self.struct._name

    @property
    def struct(self) -> "Structure":
        return self._struct

    @property
    def need(self) -> str:
        return self._need

    @property
    def required(self) -> bool:
        return self._need == REQUIRED

    @property
    def optional(self) -> bool:
        return self._need == OPTIONAL

    @property
    def multiplicity(self) -> str:
        return self._multiplicity

    @property
    def repeatable(self) -> bool:
        return self._multiplicity == REPEATABLE

    @property
    def non_repeatable(self) -> bool:
        return self._multiplicity == SINGLE

    @property
    def duplicability(self) -> str:
        return self._duplicability

    @property
    def unique(self) -> bool:
        return self._duplicability == UNIQUE

    @property
    def duplicable(self) -> bool:
        return self._duplicability == DUPLICABLE

    @property
    def parent(self) -> Union[None, "Structure"]:
        return self._parent

    @parent.setter
    def parent(self, parent: "Structure"):
        self._parent = parent

    @property
    def root(self) -> "Structure":
        """
        Returns the root structure, which is the first ancestral structure that does not itself have a parent.

        If the structure has no parent, then it is the root, and so the structure itself is returned.
        """
        if self.parent is None:
            return self.struct
        else:
            return self.parent._ref.root

    @property
    def path(self) -> list[str]:
        """
        Returns the path to this structure from the root structure as a list of names.

        Note that the name of the root structure is not included; this is the path from the root structure TO this
        point

        Therefore, if this structure is the root structure, the path is an empty list.

        :return:
        """
        if self.parent is None or not hasattr(self.parent, '_ref'):
            return []
        parent_path = self.parent._ref.path
        parts = parent_path + [self.struct._name]
        return parts

    @property
    def all_required(self) -> list[Union["Field", "Structure"]]:
        """
        Return all fields and structures which are required in this structure
        :return:
        """
        return [f for f in self.struct.__dict__.values() if unity.is_required(f)]

    @property
    def structures(self) -> list["Structure"]:
        """
        Return all structures contained in this structure
        :return:
        """
        return [f for f in self.struct.__dict__.values() if isinstance(f, Structure)]

    @property
    def all_names(self) -> list[str]:
        """
        Return the names of all fields and structures in this structure
        :return:
        """
        return [unity.name(f) for f in self.all]

    @property
    def fields(self) -> list[Field]:
        """
        Return all fields contained in this structure
        :return:
        """
        return [f for f in self.struct.__dict__.values() if isinstance(f, Field)]

    @property
    def all(self) -> list[Union[Field, "Structure"]]:
        """
        Returns all fields and structures in the structure
        """
        return [f for f in self.struct.__dict__.values() if isinstance(f, (Field, Structure))]

    def by_name(self, name:str) -> Union[Field, "Structure", None]:
        """
        Return the field or structure with the given name, or None if not found.  If multiple fields or structures
        are found with the same name, a ValueError is raised.
        :param name:
        :return:
        """
        options = [f for f in self.all if unity.name(f) == name]
        if len(options) == 1:
            return options[0]
        elif len(options) > 1:
            raise ValueError(f"Multiple fields found with name '{name}' in structure '{self.struct._name}'")
        return None

    def get_path(self, ref_str:Union[str, list[str]]) -> Union[Field, "Structure", None]:
        """
        Get a field or structure by its path, given as a dot-separated string or a list of names, relative to this
        structure.

        :param ref_str:
        :return:
        """
        if isinstance(ref_str, list):
            path = ref_str
        else:
            path = ref_str.split('.')

        ctx = self.struct
        for part in path:
            if isinstance(ctx, Field):
                raise KeyError(f"Field '{ctx.name}' does not have subfields.")
            ctx = ctx._ref.by_name(part)
            if ctx is None:
                return None
        return ctx


class Structure:
    """
    Core structure class.

    This class uses 3 "private" attributes:

    * _name: the name of the structure.  This is equivalent to the `name` property of a `Field`.
    * _ref_class: the class to use for the `_ref` property.  Defaults to `StructRef`.
    * _ref: an instance of the `_ref_class`, providing all the properties and methods for the structure.

    Use of these allows the remaining properties of the class to be the nested fields and structures, and provides
    a clean way to navigate the structure.

    For example, if you have a structure like this:

    ```
    class MyStructure:
        _name = "my_structure"
        field_a = FieldA(REQUIRED, SINGLE)
        field_b = FieldA(OPTIONAL, REPEATABLE)
        nested_structure = NestedStructure(REQUIRED, SINGLE)
    ```

    You may access the fields and structures like this:

    ```
    mine = MyStructure()
    mine.field_a
    mine.field_b
    mine.nested_structure
    ```

    The `_ref` property provides all the methods and properties you need
    to interrogate the structure using a similar API to that as you would have for a Field.  In order to use it
    you must access the "private" `_ref` property, like this:

    ```
    mine._ref.all_required
    mine._ref.structures
    mine._ref.all_names
    ```

    and so on.

    Note also that when a Structure is instantiated it will clone all its fields and nested structures, so that
    each instance is independent of any other instance.  This is what allows structures and fields to be
    easily reused in different contexts within the same codebase and execution thread.

    """
    _name:str = "_structure"
    """Name of the structure.  Subclasses should override this to provide a meaningful name."""

    _ref_class:StructRef = StructRef
    """The class to use for the structure reference.  Subclasses may override this to provide a custom reference class."""

    def __init__(self, need:str=OPTIONAL,
                 multiplicity:str=SINGLE,
                 duplicability:str=DUPLICABLE,
                 parent:"Structure"=None,
                 **kwargs):
        # separate the properties out into a reference object to keep this
        # class as clean as possible
        self._ref_obj = self._ref_class(self, need, multiplicity, duplicability, parent, **kwargs)

        # now clone all the fields and structures, and set their parent to this structure
        rebound = {}
        for attr_name, attr_value in self.__class__.__dict__.items():
            if isinstance(attr_value, Field):
                clone = unity.clone(attr_value)
                clone.parent = self
                rebound[attr_name] = clone
            elif isinstance(attr_value, Structure):
                clone = unity.clone(attr_value)
                clone._ref.parent = self
                rebound[attr_name] = clone

        # set all the cloned fields and structures onto this instance
        for k, v in rebound.items():
            setattr(self, k, v)

    @property
    def _ref(self) -> StructRef:
        return self._ref_obj


class Coerce:
    def __init__(self, *args, **kwargs):
        pass

    def coerce(self, val, field):
        pass

class Validator:
    def __init__(self, *args, **kwargs):
        pass

    def validate(self, val, field, data):
        pass

    def html_attrs(self, attrs):
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
