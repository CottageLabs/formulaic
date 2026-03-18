from collections.abc import Callable
from typing import Optional, Union, Any

from formulaic import engine
from formulaic.core import Field, FieldCapability, StructureCapability, Structure
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser

class GenericFormStructureCapability(StructureCapability):
    order: list[str] = []

    def get_in_order(self):
        for name in self.order:
            entry = self.struct_ref.by_name(name)
            if entry is None:
                continue
            if isinstance(entry, Field):
                if entry.has_capability(FormFieldCapability):
                    yield entry
            elif isinstance(entry, Structure):
                if entry.ref_.has_capability(FieldsetCapability):
                    yield entry
                elif entry.ref_.has_capability(CompoundFieldCapability):
                    yield entry
            # if it doesn't match a form capability, we skip over it

class FormCapability(GenericFormStructureCapability):
    render_class = None # FormRenderer
    action: Optional[str] = None
    method: str = "post"
    use_form_in_name = False
    use_fieldsets_in_name = False
    separator = "-"


class CompoundFieldCapability(GenericFormStructureCapability):
    label = "Compound"
    repeatable = None
    conditional = False
    js = []
    group_render_class = None

class FieldsetCapability(GenericFormStructureCapability):
    label = "Fieldset"

class FormFieldCapability(FieldCapability):
    label:str = "Field"
    control_class = None # FormControl

    options:Union[list[dict[str, str]], Callable] = []
    """
    A list of option objects with a `value` and a `label` field, such as
    
    ```
    options = [
        {"value": "y", "label": "Yes"},
        {"value": "n", "label": "No"}
    ]
    ```
    """

    default:Any = None
    placeholder:str = None
    js:list[str] = []
    attributes:dict[str,str] = {}
    disabled:bool = False
    multivalue:bool = False
    repeatable = None
    conditional:bool = False
    field_render_class = None
    control_render_class = None

    def __init__(self, **kwargs):
        self._control_instance = None
        self._options_from_fn = None
        super().__init__()

    def get_control(self):
        if self._control_instance is not None:
            return self._control_instance
        if self.control_class is None:
            raise ValueError(f"Field control not defined on {self.field.__class__}")
        self._control_instance = self.control_class(self)
        return self._control_instance

    def get_options(self):
        if isinstance(self.options, list):
            return self.options
        elif self._options_from_fn is not None:
            return self._options_from_fn
        elif callable(self.options):
            self._options_from_fn = self.options()
            return self._options_from_fn
        return []


class FormSerialiser(Serialiser):
    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)

        # First stage of serialising the form is to get the data itself into a pure
        # k/v dictionary
        kvs = data_to_kv(data, struct)

        form_cap = struct.ref_.get_capability(FormCapability)

        repr = {
            "ref": form_cap,
            "elements": []
        }

        ordered_elements = form_cap.get_in_order()

        def recurse(ordered_elements, container):
            for element in ordered_elements:
                if isinstance(element, Field):
                    cap = element.get_capability(FormFieldCapability)
                    control = cap.get_control()
                    inl = control.inputs_and_labels(kvs)
                    erepr = {
                        "type": "field",
                        "ref": cap,
                        "control": inl
                    }
                    container.append(erepr)
                else:
                    if element.ref_.has_capability(FieldsetCapability):
                        cap = element.ref_.get_capability(FieldsetCapability)
                        erepr = {
                            "type": "fieldset",
                            "ref": cap,
                            "elements": []
                        }
                        container.append(erepr)
                        next_ordered_elements = cap.get_in_order()
                        recurse(next_ordered_elements, erepr["elements"])
                    elif element.ref_.has_capability(CompoundFieldCapability):
                        cap = element.ref_.get_capability(CompoundFieldCapability)
                        erepr = {
                            "type": "compound",
                            "ref": cap,
                            "elements": []
                        }
                        container.append(erepr)
                        next_ordered_elements = cap.get_in_order()
                        recurse(next_ordered_elements, erepr["elements"])

        recurse(ordered_elements, repr["elements"])

        return repr


def data_to_kv(data:dict, struct:Structure, use_form_in_name=False, use_fieldsets_in_name=False, separator="-"):
    kvs = {}

    def recurse(prefix, data, struct):
        for field in struct.ref_.fields:
            if field.repeatable:
                vals = engine.get_list(field, data)
                if len(vals) > 0:
                    for i, val in enumerate(vals):
                        kvs[prefix + field.name + separator + str(i)] = val
                else:
                    kvs[prefix + field.name + separator + "0"] = None
            else:
                kvs[prefix + field.name] = engine.get_single(field, data)

        for substruct in struct.ref_.structures:
            if substruct.ref_.has_capability(FieldsetCapability):
                new_prefix = prefix
                if use_fieldsets_in_name:
                    new_prefix = prefix + substruct.name_ + separator
                recurse(new_prefix, data, substruct)

            else:
                new_prefix = prefix + substruct.name_ + separator
                if substruct.ref_.repeatable:
                    objs = engine.get_list(substruct, data)
                    if len(objs) > 0:
                        for i, obj in enumerate(objs):
                            new_prefix = new_prefix + str(i) + separator
                            recurse(new_prefix, obj, substruct.ref_.detach())    # Make a detached substruct, which rebases the struct to the data
                    else:
                        new_prefix = new_prefix + "0" + separator
                        recurse(new_prefix, {}, substruct)
                else:
                    obj = engine.get_single(substruct, data)
                    recurse(new_prefix, obj, substruct)

    prefix = ""
    if use_form_in_name:
        prefix = struct.name_ + separator

    recurse(prefix, data, struct)
    return kvs