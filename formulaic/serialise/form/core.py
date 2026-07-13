from collections.abc import Callable
from typing import Optional, Union, Any, Generic, TypeVar, cast

from formulaic import engine
from formulaic.core import Field, FieldCapability, StructureCapability, Structure, DataProcessingResult, ErrorCode
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser


class DefaultRendererFactory:
    @staticmethod
    def get(capability) -> Optional[Callable]:
        if isinstance(capability, FormCapability):
            from formulaic.serialise.form.render import DefaultFormHTML
            return DefaultFormHTML
        elif isinstance(capability, FieldsetCapability):
            from formulaic.serialise.form.render import DefaultFieldsetHTML
            return DefaultFieldsetHTML
        elif isinstance(capability, CompoundFieldCapability):
            from formulaic.serialise.form.render import DefaultCompoundHTML
            return DefaultCompoundHTML
        elif isinstance(capability, FieldCapability):
            from formulaic.serialise.form.render import DefaultFieldHTML
            return DefaultFieldHTML
        return None

######################################
## Capabilities that each layer of the form may wish to have

class GenericFormStructureCapability(StructureCapability):
    label = "Generic"
    order: list[str] = []
    attributes: dict[str, str] = {}
    list_render_class = None
    render_class = None
    error_messages: dict[ErrorCode, Union[str, Callable]] = {}
    """Map from error codes to messages: either a plain string, or a function which can be called with the error code instance"""

    def __init__(self):
        super().__init__()
        self._list_renderer = None
        self._renderer = None

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

    def get_renderer(self):
        if self._renderer is not None:
            return self._renderer
        rc = self.render_class
        if rc is None:
            rc = DefaultRendererFactory.get(self)
        if rc is None:
            raise ValueError(f"Renderer not defined on {self.__class__}")
        self._renderer = rc()
        return self._renderer

    def get_list_renderer(self):
        if self._list_renderer is not None:
            return self._list_renderer
        rc = self.list_render_class
        if rc is None:
            from formulaic.serialise.form.render import DefaultElementListHTML
            rc = DefaultElementListHTML
        self._list_renderer = rc()
        return self._list_renderer

    def error_message(self, error_code):
        msg = self.error_messages.get(error_code.__class__)
        if msg is None:
            return error_code.id
        if isinstance(msg, str):
            return msg
        if isinstance(msg, Callable):
            return msg(error_code)
        return ""


class FormCapability(GenericFormStructureCapability):
    label = "Form"
    action: Optional[str] = None
    method: str = "post"

    use_form_in_name = False
    use_fieldsets_in_name = False
    separator = "-"


class FieldsetCapability(GenericFormStructureCapability):
    label = "Fieldset"


class CompoundFieldCapability(GenericFormStructureCapability):
    label = "Compound"

    repeatable_label = "Compounds"
    repeatable_minimum = 1
    repeatable_initial = 1
    """Field which are bound to their structure with a REPEATABLE option can use these two properties to control how 
        many instances of the field are rendered by default, and the minimum number of displayed fields"""
    conditional = False
    js = []


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

    error_messages:dict[ErrorCode, Union[str, Callable]] = {}
    """Map from error codes to messages: either a plain string, or a function which can be called with the error code instance"""

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

    control_class:Callable = None  # FormControl, no default
    """Class responsible for representing the form field"""

    render_class = None # DefaultFieldHTML
    """Class which will render this form field, including all its controls and labels"""

    control_render_class = None # DefaultControlHTML
    """Class which will render the control itsef"""

    list_render_class = None    # DefaultElementListHTML
    """Class which will render a list of this field, if it is repeatable"""

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
            rc = DefaultRendererFactory.get(self)
        if rc is None:
            raise ValueError(f"Renderer not defined on {self.__class__}")
        rc = cast(Callable, rc)
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

    def error_message(self, error_code:ErrorCode):
        msg = self.error_messages.get(error_code.__class__)
        if msg is None:
            return error_code.id
        if isinstance(msg, str):
            return msg
        msg = msg(error_code)
        return msg

#############################################
## Model classes to offer a representation of the form as it should be rendered

AnyContainerCapability = Union[GenericFormStructureCapability, FormFieldCapability]
TElementCapability = TypeVar("TElementCapability", bound=AnyContainerCapability)

class ElementContainerRepresentation(Generic[TElementCapability]):
    def __init__(self, capability: TElementCapability, prefix="", elements=None, parent=None, error_codes=None):
        self._capability = capability
        self._prefix = prefix
        self._elements = elements or []
        self._parent = parent
        self._error_codes = error_codes or []

    @property
    def capability(self):
        return self._capability

    @property
    def prefix(self):
        return self._prefix

    @property
    def errors(self):
        return self._error_codes

    @property
    def displayable_errors(self):
        return [e for e in self._error_codes if
                e.__class__ not in self._capability.error_messages or
                self._capability.error_messages.get(e.__class__) is not False]

    def has_nested_errors(self):
        if len(self._error_codes) > 0:
            return True
        for element in self.elements:
            if isinstance(element, ElementContainerRepresentation):
                if element.has_nested_errors():
                    return True
            elif isinstance(element, FieldRepresentation):
                if len(element.errors) > 0:
                    return True
        return False

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def elements(self):
        return self._elements

    def add_element(self, element):
        element.parent = self
        self._elements.append(element)

    #########################################
    ## utilities to aid rendering

    @property
    def renderer(self):
        return self._capability.get_renderer()

    @property
    def attributes(self):
        return self._capability.attributes

    @property
    def name(self):
        if isinstance(self._capability, FormFieldCapability):
            return self._capability.field.name
        return str(getattr(self._capability.struct_ref, "name", ""))

    @property
    def label(self):
        return self._capability.label

    def error_message(self, error_code:ErrorCode):
        return self._capability.error_message(error_code)

class FormRepresentation(ElementContainerRepresentation[FormCapability]):
    @property
    def action(self):
        return self._capability.action

    @property
    def method(self):
        return self._capability.method

class ListRepresentation(ElementContainerRepresentation[AnyContainerCapability]):
    @property
    def renderer(self):
        return self._capability.get_list_renderer()

    @property
    def repeatable_label(self):
        label = self._capability.repeatable_label
        if not label:
            label = self._capability.label
        return label

class FieldsetRepresentation(ElementContainerRepresentation[FieldsetCapability]):
    pass

class CompoundRepresentation(ElementContainerRepresentation[CompoundFieldCapability]):
    pass

class FieldRepresentation:
    def __init__(self, capability:FormFieldCapability, prefix="", control=None, parent=None, error_codes=None):
        self._capability = capability
        self._prefix = prefix
        self._control = control or []
        self._parent = parent
        self._error_codes = error_codes or []

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def capability(self):
        return self._capability

    @property
    def prefix(self):
        return self._prefix

    @property
    def control(self):
        return self._control

    @property
    def errors(self):
        return self._error_codes

    @property
    def displayable_errors(self):
        return [e for e in self._error_codes if
                e.__class__ not in self._capability.error_messages or
                self._capability.error_messages.get(e.__class__) is not False]

    #########################################
    ## utilities to aid rendering

    @property
    def control_renderer(self):
        return self._capability.get_control_renderer()

    @property
    def required(self):
        return self._capability.field.required

    @property
    def renderer(self):
        return self._capability.get_renderer()

    @property
    def attributes(self):
        return self._capability.attributes

    @property
    def name(self):
        return self._capability.field.name

    @property
    def label(self):
        return self._capability.label

    def error_message(self, error_code:ErrorCode):
        return self._capability.error_message(error_code)

###########################################
## Form serialiser
##
## This serialiser can turn data and a struct into a tree
## of elements and their properties for rendering

class FormSerialiser(Serialiser):
    def make_id(self, struct, path, data_context=None):
        if data_context is None:
            data_context = []

        form_cap = struct.ref_.get_capability(FormCapability)

        id = ""
        if form_cap.use_form_in_name:
            id = struct.name_ + form_cap.separator

        ctx = struct
        for i, p in enumerate(path):
            next = ctx.ref_.by_name(p)
            if isinstance(next, Field):
                cap = next.get_capability(FormFieldCapability)
                if next.repeatable and not cap.multiple:
                    id += next.name + form_cap.separator
                    id += str(data_context[i]) if len(data_context) > i else "0"
                else:
                    id += next.name
                # We return here because you can't go lower than the field, but it's possible
                # the request is garbled, and we ought to check it and throw an error
                return id
            else:
                if next.ref_.has_capability(FieldsetCapability):
                    if form_cap.use_fieldsets_in_name:
                        id += next.name_ + form_cap.separator
                elif next.ref_.has_capability(CompoundFieldCapability):
                    id += next.name_ + form_cap.separator
                    if next.ref_.repeatable:
                        id += str(data_context[i]) if len(data_context) > i else "0"
                        id += form_cap.separator
            ctx = next
        return id

    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin],
                               struct:Optional[Structure]=None,
                               errors:Optional[DataProcessingResult]=None,
                               **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)
        form_cap = struct.ref_.get_capability(FormCapability)
        if errors is None:
            # for convenience, make an empty DPR so we can avoid a lot of None checks
            errors = DataProcessingResult()

        form_errors = errors.error_codes_for(struct)
        repr = FormRepresentation(form_cap, error_codes=form_errors)

        if form_cap.use_form_in_name:
            repr.prefix = struct.name_ + form_cap.separator

        ordered_elements = form_cap.get_in_order()

        def recurse(prefix, data, ordered_elements, representation):
            for element in ordered_elements:
                if isinstance(element, Field):
                    # Handle a form field
                    # * May be repeatable
                    # * May have zero or more values
                    cap = element.get_capability(FormFieldCapability)
                    control = cap.get_control()

                    if element.repeatable and not cap.multiple:
                        # if the element is repeatable, we want to render multiple controls
                        # EXCEPT if the field is a multiple field, meaning a single control will handle multiple inputs
                        # If you want a repeatable multi-input, you will need to nest the field in another repeatable container
                        new_prefix = prefix + element.name + form_cap.separator
                        error_codes = errors.error_codes_for(element)
                        rrepr = ListRepresentation(cap, prefix=new_prefix, error_codes=error_codes)
                        representation.add_element(rrepr)

                        vals = engine.get_list(element, data)
                        if len(vals) > 0:
                            for i, val in enumerate(vals):
                                index_prefix = new_prefix + str(i)
                                inl = control.inputs_and_labels(index_prefix, val)
                                erepr = FieldRepresentation(cap, prefix=index_prefix, control=inl, error_codes=error_codes)
                                rrepr.add_element(erepr)

                            remaining = cap.repeatable_initial - len(vals)
                            if remaining > 0:
                                for i in range(len(vals), cap.repeatable_initial):
                                    index_prefix = new_prefix + str(i)
                                    inl = control.inputs_and_labels(index_prefix, None)
                                    erepr = FieldRepresentation(cap, prefix=new_prefix, control=inl)
                                    rrepr.add_element(erepr)
                        else:
                            target = cap.repeatable_initial
                            for i in range(target):
                                index_prefix = new_prefix + str(i)
                                inl = control.inputs_and_labels(index_prefix, None)
                                erepr = FieldRepresentation(cap, prefix=new_prefix, control=inl)
                                rrepr.add_element(erepr)
                    else:
                        new_prefix = prefix + element.name
                        val = engine.get_single(element, data) # this will still return a list if the value is a list
                        inl = control.inputs_and_labels(new_prefix, val)
                        error_codes = errors.error_codes_for(element)
                        erepr = FieldRepresentation(cap, prefix=new_prefix, control=inl, error_codes=error_codes)
                        representation.add_element(erepr)
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
                        error_codes = errors.error_codes_for(element)
                        erepr = FieldsetRepresentation(cap, prefix=new_prefix, error_codes=error_codes)
                        representation.add_element(erepr)

                        next_ordered_elements = cap.get_in_order()
                        recurse(new_prefix, data, next_ordered_elements, erepr)

                    elif element.ref_.has_capability(CompoundFieldCapability):
                        cap = element.ref_.get_capability(CompoundFieldCapability)
                        new_prefix = prefix + element.name_ + form_cap.separator

                        if element.ref_.repeatable:
                            error_codes = errors.error_codes_for(element)
                            rrepr = ListRepresentation(cap, prefix=new_prefix, error_codes=error_codes)
                            representation.add_element(rrepr)

                            objs = engine.get_list(element, data)
                            if len(objs) > 0:
                                next_ordered_elements = cap.get_in_order(detach=True)
                                for i, obj in enumerate(objs):
                                    index_prefix = new_prefix + str(i) + form_cap.separator
                                    erepr = CompoundRepresentation(cap, prefix=index_prefix, error_codes=error_codes)
                                    rrepr.add_element(erepr)
                                    recurse(index_prefix, obj, next_ordered_elements, erepr)

                                remaining = cap.repeatable_initial - len(objs)
                                if remaining > 0:
                                    for i in range(len(objs), cap.repeatable_initial):
                                        index_prefix = new_prefix + str(i) + form_cap.separator
                                        erepr = CompoundRepresentation(cap, prefix=index_prefix)
                                        rrepr.add_element(erepr)
                                        recurse(index_prefix, {}, next_ordered_elements, erepr)
                            else:
                                next_ordered_elements = cap.get_in_order()
                                target = cap.repeatable_initial
                                error_codes = errors.error_codes_for(element)
                                for i in range(target):
                                    index_prefix = new_prefix + str(i) + form_cap.separator
                                    erepr = CompoundRepresentation(cap, prefix=new_prefix, error_codes=error_codes)
                                    rrepr.add_element(erepr)
                                    recurse(index_prefix, data, next_ordered_elements, erepr)
                        else:
                            error_codes = errors.error_codes_for(element)
                            erepr = CompoundRepresentation(cap, prefix=new_prefix, error_codes=error_codes)
                            representation.add_element(erepr)
                            next_ordered_elements = cap.get_in_order()
                            recurse(new_prefix, data, next_ordered_elements, erepr)

        recurse(repr.prefix, data, ordered_elements, repr)
        return repr

    def representation_to_string(self, representation:FormRepresentation, **kwargs):
        form_cap = representation.capability
        form_renderer = form_cap.get_renderer()
        html = form_renderer.draw(representation, **kwargs)
        return html


########################################
## Form Data parser
##
## This works from data that you would get back from a form (the representation)
## and the true model data.
##
## Note that it is NOT the opposite of FormSerialiser, as this does not
## Interpret a full HTML form, only the data that comes back from such a form

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
                    cap = element.get_capability(FormFieldCapability)
                    if element.repeatable and not cap.multiple:
                        new_prefix = prefix + element.name + form_cap.separator
                        vals = extract_to_list_by_prefix(new_prefix, representation)
                        if len(vals) > 0:
                            data[element.name] = vals
                    else:
                        new_prefix = prefix + element.name
                        # extract the exact value
                        val = representation.get(new_prefix)    # this may return a list or not
                        if val:
                            if cap.multiple and not isinstance(val, list):
                                val = [val]
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

##############################################
## Form Object, to pull all the bits together

class FormObject(FormulaicObject):
    apply_structure_on_init = False
    check_required_on_init = False
    check_required_on_set = False

    def __init__(self, data=None, **kwargs):
        super(FormObject, self).__init__(data=data)
        self._validation_result = DataProcessingResult()

    def validate(self) -> bool:
        self._validation_result = engine.validate(self.data, self.struct)
        return self._validation_result.is_valid

    @property
    def is_valid(self):
        return self._validation_result.is_valid

    @property
    def validation_result(self):
        return self._validation_result