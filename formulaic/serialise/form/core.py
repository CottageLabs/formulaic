from collections.abc import Callable
from copy import deepcopy
from typing import Optional, Union, Any

from formulaic import engine
from formulaic.core import Field, FieldCapability, StructureCapability, Structure
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser


class GenericFormStructureCapability(StructureCapability):
    order: list[str] = []

    def get_in_order(self, detach=False):
        for name in self.order:
            entry = self.struct_ref.struct.__getattribute__(name)
            if entry is None:
                continue
            if isinstance(entry, Field):
                if entry.has_capability(FormFieldCapability):
                    if detach:
                        yield entry.detach()
                    else:
                        yield entry
            elif isinstance(entry, Structure):
                if entry.ref_.has_capability(FieldsetCapability):
                    if detach:
                        yield entry.ref_.detach()
                    else:
                        yield entry
                elif entry.ref_.has_capability(CompoundFieldCapability):
                    if detach:
                        yield entry.ref_.detach()
                    else:
                        yield entry
            # if it doesn't match a form capability, we skip over it


class FormCapability(GenericFormStructureCapability):
    action: Optional[str] = None
    method: str = "post"
    attributes:dict[str,str] = {}

    use_form_in_name = False
    use_fieldsets_in_name = False
    separator = "-"

    render_class = None  # FormRenderer

    def __init__(self):
        super().__init__()
        self._renderer = None

    def get_renderer(self):
        if self._renderer is not None:
            return self._renderer
        rc = self.render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultFormHTML
            rc = DefaultFormHTML
        self._renderer = rc()
        return self._renderer


class CompoundFieldCapability(GenericFormStructureCapability):
    label = "Compound"
    repeatable = None
    conditional = False
    js = []
    attributes: dict[str, str] = {}

    render_class = None

    def __init__(self):
        super().__init__()
        self._renderer = None

    def get_renderer(self):
        if self._renderer is not None:
            return self._renderer
        rc = self.render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultCompoundHTML
            rc = DefaultCompoundHTML
        self._renderer = rc()
        return self._renderer

class FieldsetCapability(GenericFormStructureCapability):
    label = "Fieldset"
    attributes:dict[str,str] = {}

    render_class = None

    def __init__(self):
        super().__init__()
        self._renderer = None

    def get_renderer(self):
        if self._renderer is not None:
            return self._renderer
        rc = self.render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultFieldsetHTML
            rc = DefaultFieldsetHTML
        self._renderer = rc()
        return self._renderer

class FormFieldCapability(FieldCapability):
    label:str = "Field"

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

    control_class = None  # FormControl
    render_class = None
    control_render_class = None

    def __init__(self, **kwargs):
        self._control_instance = None
        self._options_from_fn = None
        self._renderer = None
        self._control_renderer = None
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

    def get_renderer(self):
        if self._renderer is not None:
            return self._renderer
        rc = self.render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultFieldHTML
            rc = DefaultFieldHTML
        self._renderer = rc()
        return self._renderer

    def get_control_renderer(self):
        if self._control_renderer is not None:
            return self._control_renderer
        rc = self.control_render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultControlHTML
            rc = DefaultControlHTML
        self._control_renderer = rc()
        return self._control_renderer


class FormSerialiser(Serialiser):
    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)

        # First stage of serialising the form is to get the data itself into a pure
        # k/v dictionary
        # kvs = data_to_kv(data, struct)

        form_cap = struct.ref_.get_capability(FormCapability)

        repr = {
            "ref": form_cap,
            "prefix": "",
            "elements": []
        }

        if form_cap.use_form_in_name:
            repr["prefix"] = struct.name_ + form_cap.separator

        ordered_elements = form_cap.get_in_order()

        def recurse(prefix, data, ordered_elements, container):
            for element in ordered_elements:
                if isinstance(element, Field):
                    # Handle a form field
                    # * May be repeatable
                    # * May have zero or more values
                    cap = element.get_capability(FormFieldCapability)
                    control = cap.get_control()

                    if element.repeatable:
                        new_prefix = prefix + element.name + form_cap.separator
                        vals = engine.get_list(element, data)
                        if len(vals) > 0:
                            for i, val in enumerate(vals):
                                index_prefix = new_prefix + str(i)
                                inl = control.inputs_and_labels(index_prefix, val)

                                erepr = {
                                    "type": "field",
                                    "ref": cap,
                                    "prefix": index_prefix,
                                    "control": inl
                                }
                                container.append(erepr)
                        else:
                            new_prefix = new_prefix + "0"
                            inl = control.inputs_and_labels(new_prefix, None)

                            erepr = {
                                "type": "field",
                                "ref": cap,
                                "prefix": new_prefix,
                                "control": inl
                            }
                            container.append(erepr)
                    else:
                        new_prefix = prefix + element.name
                        val = engine.get_single(element, data)
                        inl = control.inputs_and_labels(new_prefix, val)

                        erepr = {
                            "type": "field",
                            "ref": cap,
                            "prefix": new_prefix,
                            "control": inl
                        }
                        container.append(erepr)
                else:
                    if element.ref_.has_capability(FieldsetCapability):
                        # Handle a fieldset.
                        # * Fieldsets may or may not contribute to the ID prefix
                        # * Fieldsets are not repeatable components of a form
                        # * We do not need to retrieve the data from a field
                        new_prefix = prefix
                        if form_cap.use_fieldsets_in_name:
                            new_prefix = prefix + element.name_ + form_cap.separator

                        cap = element.ref_.get_capability(FieldsetCapability)

                        erepr = {
                            "type": "fieldset",
                            "prefix": new_prefix,
                            "ref": cap,
                            "elements": []
                        }
                        container.append(erepr)

                        next_ordered_elements = cap.get_in_order()
                        recurse(new_prefix, data, next_ordered_elements, erepr["elements"])

                    elif element.ref_.has_capability(CompoundFieldCapability):
                        cap = element.ref_.get_capability(CompoundFieldCapability)
                        new_prefix = prefix + element.name_ + form_cap.separator

                        if element.ref_.repeatable:
                            erepr = {
                                "type": "compound",
                                "prefix": new_prefix,
                                "ref": cap,
                                "elements": []
                            }
                            container.append(erepr)

                            objs = engine.get_list(element, data)
                            if len(objs) > 0:
                                next_ordered_elements = cap.get_in_order(detach=True)
                                for i, obj in enumerate(objs):
                                    index_prefix = new_prefix + str(i) + form_cap.separator
                                    recurse(index_prefix, obj, next_ordered_elements, erepr["elements"])
                            else:
                                next_ordered_elements = cap.get_in_order()
                                index_prefix = new_prefix + "0" + form_cap.separator
                                recurse(index_prefix, data, next_ordered_elements, erepr["elements"])
                        else:
                            erepr = {
                                "type": "compound",
                                "ref": cap,
                                "prefix": new_prefix,
                                "elements": []
                            }
                            container.append(erepr)

                            next_ordered_elements = cap.get_in_order()
                            recurse(new_prefix, data, next_ordered_elements, erepr["elements"])

        recurse(repr["prefix"], data, ordered_elements, repr["elements"])

        return repr

    def representation_to_string(self, representation:dict, **kwargs):
        form_cap = representation.get("ref")
        form_renderer = form_cap.get_renderer()
        html = form_renderer.draw(representation)
        return html

# def data_to_kv(data:dict, struct:Structure, use_form_in_name=False, use_fieldsets_in_name=False, separator="-"):
#     kvs = {}
#
#     def recurse(prefix, data, struct):
#         for field in struct.ref_.fields:
#             if field.repeatable:
#                 vals = engine.get_list(field, data)
#                 if len(vals) > 0:
#                     for i, val in enumerate(vals):
#                         kvs[prefix + field.name + separator + str(i)] = val
#                 else:
#                     kvs[prefix + field.name + separator + "0"] = None
#             else:
#                 kvs[prefix + field.name] = engine.get_single(field, data)
#
#         for substruct in struct.ref_.structures:
#             if substruct.ref_.has_capability(FieldsetCapability):
#                 new_prefix = prefix
#                 if use_fieldsets_in_name:
#                     new_prefix = prefix + substruct.name_ + separator
#                 recurse(new_prefix, data, substruct)
#
#             else:
#                 new_prefix = prefix + substruct.name_ + separator
#                 if substruct.ref_.repeatable:
#                     objs = engine.get_list(substruct, data)
#                     if len(objs) > 0:
#                         for i, obj in enumerate(objs):
#                             new_prefix = new_prefix + str(i) + separator
#                             recurse(new_prefix, obj, substruct.ref_.detach())    # Make a detached substruct, which rebases the struct to the data
#                     else:
#                         new_prefix = new_prefix + "0" + separator
#                         recurse(new_prefix, {}, substruct)
#                 else:
#                     obj = engine.get_single(substruct, data)
#                     recurse(new_prefix, obj, substruct)
#
#     prefix = ""
#     if use_form_in_name:
#         prefix = struct.name_ + separator
#
#     recurse(prefix, data, struct)
#     return kvs