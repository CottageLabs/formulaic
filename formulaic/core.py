from copy import deepcopy
from typing import Union, Callable, Tuple, Any

from formulaic.lib import unity, introspection

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

    serialiser:Callable = None
    """A function that can take the value of the field and produce a primitive value suitable for serialisation, e.g. to JSON or XML."""

    capabilities:tuple["FieldCapability"] = ()

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
        if need not in [REQUIRED, OPTIONAL]:
            raise ValueError(f"Invalid need value: {need}. Must be '{REQUIRED}' or '{OPTIONAL}'")
        if multiplicity not in [SINGLE, REPEATABLE]:
            raise ValueError(f"Invalid multiplicity value: {multiplicity}. Must be '{SINGLE}' or '{REPEATABLE}'")
        if duplicability not in [UNIQUE, DUPLICABLE]:
            raise ValueError(f"Invalid duplicability value: {duplicability}. Must be '{UNIQUE}' or '{DUPLICABLE}'")

        self._need = need
        self._multiplicity = multiplicity
        self._duplicability = duplicability
        self._parent = parent

        self._capabilities = []
        for cap in self._collect_class_capabilities():
            self.add_capability(cap)

        if check_coherence:
            self._check_coherence()

    @classmethod
    def _collect_class_capabilities(cls):
        result = []
        for base in reversed(cls.__mro__):
            result.extend(getattr(base, "capabilities", ()))
        return result

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

    def has_allowed_range(self) -> bool:
        return len(self.allowed_range) == 2

    def has_allowed_values(self) -> bool:
        return len(self.allowed_values) > 0

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
            return self.parent.ref_.root

    @property
    def path(self) -> list[str]:
        """
        Returns the path to this field from the root structure as a list of names.
        :return:
        """
        parts = [self.name]
        if self.parent is not None:
            parent_path = self.parent.ref_.path
            parts = parent_path + parts
        return parts

    @property
    def stack(self) -> list[Union["Field", "Structure"]]:
        """
        Returns the stack of fields and structures from the root structure to this field as a list of objects.
        :return:
        """
        parts = [self]
        if self.parent is not None:
            parent_stack = self.parent.ref_.stack
            parts = parent_stack + parts
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
        if self.has_allowed_values() and self.has_allowed_range():
            msg.append(f"Cannot have both allowed_values and allowed_range set. Choose one or the other.")

        if len(msg) > 0:
            raise ValueError("Coherence check failed for field `{}`: {}".format(self.name, "; ".join(msg)))

    def clone(self):
        """
        Clone the Field, returning a new instance with the same properties.

        Subclasses of Field that add features will need to override this method to ensure the
        clones are suitable
        """
        new = self.__class__(need=self.need, multiplicity=self.multiplicity,
                              duplicability=self.duplicability, parent=self.parent)
        new._capabilities = []
        for cap in self._capabilities:
            new.add_capability(cap.clone())
        return new

    def detach(self):
        new = self.__class__(need=self.need, multiplicity=self.multiplicity,
                             duplicability=self.duplicability, parent=None)
        new._capabilities = []
        for cap in self._capabilities:
            new.add_capability(cap.clone())
        return new

    def get_capability(self, capability_class:"FieldCapability.__class__"):
        """
        Get the extension of the field for the given extension class, or None if not found.
        If there are multiple matches, it gets the first one.

        :param capability_class: The class of the extension to get.
        :return: The extension instance, or None if not found.
        """
        for cap in self._capabilities:
            if isinstance(cap, capability_class):
                return cap
        return None

    def add_capability(self, capability:"FieldCapability"):
        """
        Add an extension to the field.

        :param capability: The extension instance to add.
        """
        self._capabilities.append(capability)
        capability.bind(self)
        return self

    def remove_capability(self, capability_class:"FieldCapability.__class__"):
        """
        Remove an extension from the field by its class.  Removes all capabilities which match the
        given class

        :param capability_class: The class of the extension to remove.
        """
        removes = []
        for i, cap in enumerate(self._capabilities):
            if isinstance(cap, capability_class):
                removes.append(i)
        for i in reversed(removes):
            del self._capabilities[i]

    def has_capability(self, capability_class:"FieldCapability.__class__") -> bool:
        """
        Check if the field has an extension of the given class.

        :param capability_class: The class of the extension to check for.
        :return: True if the field has an extension of the given class, False otherwise.
        """
        return self.get_capability(capability_class) is not None

    def get_validation_chain(self):
        chain = []
        if self.required:
            from formulaic.validate.validate import Required
            chain.append(Required())
        return chain


class FieldCapability:
    def __init__(self):
        self._field = None

    @property
    def field(self) -> Field:
        return self._field

    def bind(self, field: Field):
        self._field = field

    def clone(self):
        return deepcopy(self)

class StructRef:
    """
    This class sits alongside a Structure and provides all its properties and methods.  This is to keep the Structure
    class as clean as possible, and to separate out the properties of the structure from the structure itself.

    When you want to call functional methods on the Structure, you should do this via this class, which can be
    accessed via the `ref_` property on the Structure.  The methods in this class behave as if they were methods on
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
        self._capabilities = []

        for base in reversed(self._struct.__class__.__mro__):
            for cap in getattr(base, "capabilities_", ()):
                self.add_capability(cap.clone())

    def clone(self):
        """
        Clone the inner Structure, returning a new instance with the same properties.

        Subclasses of StructRef that add features will need to override this method to ensure the
        clones are suitable
        """
        new = self._struct.__class__(need=self.need, multiplicity=self.multiplicity,
                         duplicability=self.duplicability, parent=self.parent)
        new_ref = new.ref_
        new_ref._capabilities = []
        for cap in self._capabilities:
            new_ref.add_capability(cap.clone())
        return new

    def detach(self):
        new = self._struct.__class__(need=self.need, multiplicity=self.multiplicity,
                                     duplicability=self.duplicability, parent=None)
        new_ref = new.ref_
        new_ref._capabilities = []
        for cap in self._capabilities:
            new_ref.add_capability(cap.clone())
        return new

    @property
    def name(self) -> str:
        return self.struct.name_

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
            return self.parent.ref_.root

    @property
    def path(self) -> list[str]:
        """
        Returns the path to this structure from the root structure as a list of names.

        Note that the name of the root structure is not included; this is the path from the root structure TO this
        point

        Therefore, if this structure is the root structure, the path is an empty list.

        :return:
        """
        if self.parent is None or not hasattr(self.parent, 'ref_'):
            return []
        parent_path = self.parent.ref_.path
        parts = parent_path + [self.struct.name_]
        return parts

    @property
    def stack(self) -> list["Structure"]:
        """
        Returns the stack of structures from the root structure to this structure as a list of objects.
        :return:
        """
        if self.parent is None or not hasattr(self.parent, 'ref_'):
            return [self.struct]
        parent_stack = self.parent.ref_.stack
        parts = parent_stack + [self.struct]
        return parts

    @property
    def all_required(self) -> list[Union["Field", "Structure"]]:
        """
        Return all fields and structures which are required in this structure
        :return:
        """
        return [f for _, f in introspection.attributes(self.struct) if unity.is_required(f)]

    @property
    def structures(self) -> list["Structure"]:
        """
        Return all structures contained in this structure
        :return:
        """
        return [f for _, f in introspection.attributes(self.struct) if isinstance(f, Structure)]

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
        return [f for _, f in introspection.attributes(self.struct) if isinstance(f, Field)]

    @property
    def all(self) -> list[Union[Field, "Structure"]]:
        """
        Returns all fields and structures in the structure
        """
        return [f for _, f in introspection.attributes(self.struct) if isinstance(f, (Field, Structure))]

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
            raise ValueError(f"Multiple fields found with name '{name}' in structure '{self.struct.name_}'")
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
            ctx = ctx.ref_.by_name(part)
            if ctx is None:
                return None
        return ctx

    def get_capability(self, capability_class: "StructureCapability.__class__"):
        """
        Get the extension of the field for the given extension class, or None if not found.
        If there are multiple matches, it gets the first one.

        :param capability_class: The class of the extension to get.
        :return: The extension instance, or None if not found.
        """
        for cap in self._capabilities:
            if isinstance(cap, capability_class):
                return cap
        return None

    def add_capability(self, capability: "StructureCapability"):
        """
        Add an extension to the field.

        :param capability: The extension instance to add.
        """
        self._capabilities.append(capability)
        capability.bind(self)
        return self

    def remove_capability(self, capability_class: "StructureCapability.__class__"):
        """
        Remove an extension from the field by its class.  Removes all capabilities which match the
        given class

        :param capability_class: The class of the extension to remove.
        """
        removes = []
        for i, cap in enumerate(self._capabilities):
            if isinstance(cap, capability_class):
                removes.append(i)
        for i in reversed(removes):
            del self._capabilities[i]

    def has_capability(self, capability_class:"StructureCapability.__class__") -> bool:
        """
        Check if the field has an extension of the given class.

        :param capability_class: The class of the extension to check for.
        :return: True if the field has an extension of the given class, False otherwise.
        """
        return self.get_capability(capability_class) is not None

class StructureCapability:
    def __init__(self):
        self._struct_ref = None

    def bind(self, struct_ref: StructRef):
        self._struct_ref = struct_ref

    @property
    def struct_ref(self) -> StructRef:
        return self._struct_ref

    def clone(self):
        return deepcopy(self)

class Structure:
    """
    Core structure class.

    This class uses 3 "semi-private" attributes.  These are top-level, non-private attributes of the class,
    that are intended to avoid name clashes with the fields and structures that are defined within the structure.  They
    are all suffixed with an underscore, and represent the 3 reserved attributes of the Structure object.

    They are:

    * name_: the name of the structure.  This is equivalent to the `name` property of a `Field`.
    * ref_class_: the class to use for the `ref_` property.  Defaults to `StructRef`.
    * ref_: an instance of the `ref_class_`, providing all the properties and methods for the structure.

    Use of these allows the remaining properties of the class to be the nested fields and structures, and provides
    a clean way to navigate the structure.

    For example, if you have a structure like this:

    ```
    class MyStructure:
        name_ = "my_structure"
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

    The `ref_` property provides all the methods and properties you need
    to interrogate the structure using a similar API to that as you would have for a Field.  In order to use it
    you must access the `ref_` property, like this:

    ```
    mine.ref_.all_required
    mine.ref_.structures
    mine.ref_.all_names
    ```

    and so on.

    Note also that when a Structure is instantiated it will clone all its fields and nested structures, so that
    each instance is independent of any other instance.  This is what allows structures and fields to be
    easily reused in different contexts within the same codebase and execution thread.

    """
    name_:str = "_structure"
    """Name of the structure.  Subclasses should override this to provide a meaningful name."""

    ref_class_:StructRef = StructRef
    """The class to use for the structure reference.  Subclasses may override this to provide a custom reference class."""

    validators_:list["Validator"] = []
    """Validators that apply at the structural level"""

    capabilities_ = ()
    """Capabilities that structure element has"""

    def __init__(self, need:str=OPTIONAL,
                 multiplicity:str=SINGLE,
                 duplicability:str=DUPLICABLE,
                 parent:"Structure"=None,
                 **kwargs):
        # separate the properties out into a reference object to keep this
        # class as clean as possible
        self._ref_obj = self.ref_class_(self, need, multiplicity, duplicability, parent, **kwargs)

        # now clone all the fields and structures, and set their parent to this structure
        rebound = {}
        for attr_name, attr_value in introspection.attributes(self.__class__): #self.__class__.__dict__.items():
            if isinstance(attr_value, Field):
                clone = unity.clone(attr_value)
                clone.parent = self
                rebound[attr_name] = clone
            elif isinstance(attr_value, Structure):
                clone = unity.clone(attr_value)
                clone.ref_.parent = self
                rebound[attr_name] = clone

        # set all the cloned fields and structures onto this instance
        for k, v in rebound.items():
            setattr(self, k, v)

    @property
    def ref_(self) -> StructRef:
        return self._ref_obj

###########################################
## Coercion and Validation

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

#########################################
## Exceptions and Error Handling

class DataError:
    def __init__(self, field:Union[Field, Structure], original_value, code, **kwargs):
        self.field = field
        self.original_value = original_value
        self.code = code
        self.params = kwargs

class ValidationError(DataError):
    def __init__(self, field:Union[Field, Structure], original_value, code, stop_validation=False, **kwargs):
        super().__init__(field, original_value, code, **kwargs)
        self.stop_validation = stop_validation

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

    def __str__(self):
        s = f"ErrorCode: `{self.id}`"
        return s

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

