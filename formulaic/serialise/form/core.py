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
    list_render_class = None

    def __init__(self):
        super().__init__()
        self._list_renderer = None

    def get_in_order(self, detach=False):
        return [x for x in self.ordered_iterator(detach=detach)]

    def ordered_iterator(self, detach=False):
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

    def get_list_renderer(self):
        if self._list_renderer is not None:
            return self._list_renderer
        rc = self.list_render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultElementListHTML
            rc = DefaultElementListHTML
        self._list_renderer = rc()
        return self._list_renderer


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

    repeatable_label = "Compounds"
    repeatable_minimum = 1
    repeatable_initial = 1
    """Field which are bound to their structure with a REPEATABLE option can use these two properties to control how 
        many instances of the field are rendered by default, and the minimum number of displayed fields"""
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
    """The label associated with the field"""

    options:Union[list[dict[str, str]], Callable] = None
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
    """Default value for the field.  Controls may interpret this in whichever way makes the most sense for them"""

    placeholder:str = None
    """Placeholder value for the field.  Controls may interpret this in whichever way makes the most sense for them"""

    attributes:dict[str,str] = {}
    """Attributes to attach to the main form control"""

    disabled:bool = False
    """Disable the form control"""

    multiple:bool = False
    """For fields which allow the selection of elements, do they allow for multi selections (e.g. multi-select box, or checkboxes)"""

    repeatable_label = "Fields"
    repeatable_minimum = 1
    repeatable_initial = 1
    """Field which are bound to their structure with a REPEATABLE option can use these two properties to control how 
        many instances of the field are rendered by default, and the minimum number of displayed fields"""

    conditional:bool = False

    control_class = None  # FormControl
    """Class responsible for representing the form field"""

    render_class = None
    """Class which will render this form field, including all its controls and labels"""

    control_render_class = None
    """Class which will render the control itsef"""

    list_render_class = None

    js: list[str] = []
    """List of strings or objects to be JSON serialised and passed to the front end JS"""

    def __init__(self, **kwargs):
        self._control_instance = None
        self._options_from_fn = None
        self._renderer = None
        self._control_renderer = None
        self._list_renderer = None
        super().__init__()

    def get_control(self):
        if self._control_instance is not None:
            return self._control_instance
        if self.control_class is None:
            raise ValueError(f"Field control not defined on {self.field.__class__}")
        self._control_instance = self.control_class(self)
        return self._control_instance

    def get_options(self):
        if self.options is None:
            return []
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

    def get_list_renderer(self):
        if self._list_renderer is not None:
            return self._list_renderer
        rc = self.list_render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultElementListHTML
            rc = DefaultElementListHTML
        self._list_renderer = rc()
        return self._list_renderer


class FormSerialiser(Serialiser):
    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)
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
                        rrepr = {
                            "type": "list",
                            "ref": cap,
                            "prefix": new_prefix,
                            "elements": []
                        }
                        container.append(rrepr)

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
                                rrepr["elements"].append(erepr)

                            remaining = cap.repeatable_initial - len(vals)
                            if remaining > 0:
                                for i in range(len(vals), cap.repeatable_initial):
                                    index_prefix = new_prefix + str(i)
                                    inl = control.inputs_and_labels(index_prefix, None)

                                    erepr = {
                                        "type": "field",
                                        "ref": cap,
                                        "prefix": new_prefix,
                                        "control": inl
                                    }
                                    rrepr["elements"].append(erepr)
                        else:
                            target = cap.repeatable_initial
                            for i in range(target):
                                index_prefix = new_prefix + str(i)
                                inl = control.inputs_and_labels(index_prefix, None)

                                erepr = {
                                    "type": "field",
                                    "ref": cap,
                                    "prefix": new_prefix,
                                    "control": inl
                                }
                                rrepr["elements"].append(erepr)
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
                            rrepr = {
                                "type": "list",
                                "prefix": new_prefix,
                                "ref": cap,
                                "elements": []
                            }
                            container.append(rrepr)

                            objs = engine.get_list(element, data)
                            if len(objs) > 0:
                                next_ordered_elements = cap.get_in_order(detach=True)
                                for i, obj in enumerate(objs):
                                    index_prefix = new_prefix + str(i) + form_cap.separator
                                    erepr = {
                                        "type": "compound",
                                        "prefix": index_prefix,
                                        "ref": cap,
                                        "elements": []
                                    }
                                    rrepr["elements"].append(erepr)
                                    recurse(index_prefix, obj, next_ordered_elements, erepr["elements"])

                                remaining = cap.repeatable_initial - len(objs)
                                if remaining > 0:
                                    for i in range(len(objs), cap.repeatable_initial):
                                        index_prefix = new_prefix + str(i) + form_cap.separator
                                        erepr = {
                                            "type": "compound",
                                            "ref": cap,
                                            "prefix": index_prefix,
                                            "elements": []
                                        }
                                        rrepr["elements"].append(erepr)
                                        recurse(index_prefix, {}, next_ordered_elements, erepr["elements"])
                            else:
                                next_ordered_elements = cap.get_in_order()
                                target = cap.repeatable_initial
                                for i in range(target):
                                    index_prefix = new_prefix + str(i) + form_cap.separator
                                    erepr = {
                                        "type": "compound",
                                        "ref": cap,
                                        "prefix": new_prefix,
                                        "elements": []
                                    }
                                    rrepr["elements"].append(erepr)
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


class FormDataParser(Serialiser):
    def representation_to_data(self, representation:dict, struct:Structure, **kwargs) -> dict:
        data = {}

        form_cap = struct.ref_.get_capability(FormCapability)
        prefix = ""
        if form_cap.use_form_in_name:
            prefix = struct.name_ + form_cap.separator

        def extract_to_list_by_prefix(prefix, representation):
            elements = {}
            for k, v in representation.items():
                if k.startswith(prefix):
                    suffix = k[len(prefix):]
                    idx = int(suffix)
                    elements[idx] = v

            indexes = sorted(list(elements.keys()))
            return [elements[i] for i in indexes if elements[i]]

        def extract_nested_by_prefix(prefix, separator, representation):
            elements = {}
            for k, v in representation.items():
                if k.startswith(prefix):
                    suffix = k[len(prefix):]
                    offset = suffix.index(separator)
                    idx = int(suffix[:offset])
                    onward_path = suffix[offset+1:]
                    if idx not in elements:
                        elements[idx] = {}
                    elements[idx][onward_path] = v

            indexes = sorted(list(elements.keys()))
            return [elements[i] for i in indexes]

        def recurse(prefix, representation, ordered_elements, data):
            for element in ordered_elements:
                if isinstance(element, Field):
                    if element.repeatable:
                        new_prefix = prefix + element.name + form_cap.separator
                        vals = extract_to_list_by_prefix(new_prefix, representation)
                        if len(vals) > 0:
                            data[element.name] = vals
                    else:
                        new_prefix = prefix + element.name
                        # extract the exact value
                        val = representation.get(new_prefix)
                        if val:
                            data[element.name] = val
                else:
                    if element.ref_.has_capability(FieldsetCapability):
                        # if this is a fieldset, just add the fieldset to the data model
                        # and recurse into it to see what other form fields apply to it
                        new_prefix = prefix
                        if form_cap.use_fieldsets_in_name:
                            new_prefix = prefix + element.name_ + form_cap.separator
                        cap = element.ref_.get_capability(FieldsetCapability)
                        nested = {}
                        next_ordered_elements = cap.get_in_order()
                        recurse(new_prefix, representation, next_ordered_elements, nested)
                        if len(nested) > 0:
                            data[element.name_] = nested

                    elif element.ref_.has_capability(CompoundFieldCapability):
                        cap = element.ref_.get_capability(CompoundFieldCapability)
                        new_prefix = prefix + element.name_ + form_cap.separator

                        if element.ref_.repeatable:
                            # Extract all the fields that sit within this compound field, such
                            # that we have a list of objects with all their prefixes to this point
                            # stripped, then we can recurse into each nested field with the subset of
                            # data (this is why we detach the structure at this point, to rebase on
                            # the empty prefix
                            compounds = extract_nested_by_prefix(new_prefix, form_cap.separator, representation)
                            if len(compounds) > 0:
                                next_ordered_elements = cap.get_in_order(detach=True)
                                for c in compounds:
                                    nested = {}
                                    recurse("", c, next_ordered_elements, nested)
                                    if len(nested) > 0:
                                        if element.name_ not in data:
                                            data[element.name_] = []
                                        data[element.name_].append(nested)
                        else:
                            next_ordered_elements = cap.get_in_order()
                            nested = {}
                            recurse(new_prefix, representation, next_ordered_elements, nested)
                            if len(nested) > 0:
                                data[element.name_] = nested

        ordered_elements = form_cap.get_in_order()
        recurse(prefix, representation, ordered_elements, data)

        return data