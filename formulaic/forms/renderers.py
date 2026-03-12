from typing import Union

from formulaic import engine
from formulaic.core import Structure
from formulaic.forms.core import HTMLGenerator, ContextualForm, Fieldset, FormField, FormGroup, FormInfo
from formulaic.lib import unity
from formulaic.objects import FormulaicObject, FormulaicMixin
from formulaic.serialise.core import Serialiser

class FormRepresentation(Structure):
    pass

class FormSerialiser(Serialiser):
    def data_to_representation(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct:Structure=None, **kwargs):
        mixin, fo, struct, data = unity.expand(data, struct)
        form_info:FormInfo = struct._form_info

        repr = {"type": "form", "attrs": {}, "ref": struct, "fieldsets": []}

        if form_info.action:
            repr["attrs"]["action"] = form_info.action
        if form_info.method:
            repr["attrs"]["method"] = form_info.method

        def recurse(sr, container):
            fieldsets = sr.fieldsets
            for fieldset in fieldsets:
                fsrepr = {"type": "fieldset", "attrs": {}, "fields": [], "ref": fieldset}

                fields = sr.get_fieldset_fields(fieldset)
                for field in fields:
                    if isinstance(field, FormField):
                        fieldrepr = {"type": "field", "attrs": {}, "ref": field, "controls": []}
                        val = engine.get_data(field, data)
                        control = field.get_control()
                        inls = control.inputs_and_labels()
                        fieldrepr["controls"] = inls
                        fsrepr["fields"].append(fieldrepr)

                    elif isinstance(field, FormGroup):
                        recurse(field.ref_, fsrepr["fields"])

                container.append(fsrepr)

        sr = struct.ref_
        recurse(sr, repr["fieldsets"])
        return repr

    def data_to_string(self, data:Union[dict, FormulaicObject, FormulaicMixin], struct: Structure=None, **kwargs):
        repr = self.data_to_representation(data, struct, **kwargs)
        return self.representation_to_string(repr, **kwargs)

    def representation_to_string(self, representation, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")

    def representation_to_data(self, representation, struct:Structure, **kwargs) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")

    def string_to_representation(self, string:str, struct:Structure, **kwargs) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")

####################################################
## Interface classes for the various parts of form rendering

"""
Form rendering is done via a set of renderer classes which represent each
part of the hierarchical nature of the form.  The form structure is as
follows

FORM
    |-- FIELDSET
            |-- FIELD
                |-- FORM CONTROL (may be a single control, or multiple repeated controls for a repeatable field)
            |-- GROUP
                    |-- FIELD
                    |-- GROUP (ad infinitum)

Therefore we define renderers for each layer in the hierarchy, and a renderer is responsible
for calling those lower down the hierarchy than them.

* FORM: FormRenderer
    * Responsible for rendering the <form> tag and calling each fieldset renderer
* FIELDSET: FieldsetRenderer
    * Responsible for rendering the <fieldset> tag and calling each field and group renderer
* FIELD: FieldRenderer
    * Responsible for rendering the field container (not the form control itself).  This would include
        any information about the field as a while, such as error messages, help text etc.
* FORM CONTROL: FormControlRenderer
    * Responsible for rendering the actual HTML form control(s) for a field.  This will include the actual raw
    form control and label, but may also include container and layout for a single form (e.g. placing labels in 
    front of controls, or wrapping each control/label pair in a div/span)
* GROUP: GroupRenderer
    * Responsible for rendering a group of fields (or sub groups).  This may include a container, label etc.  This
    would also then render the individual fields (using a FieldRenderer) or sub groups (using a GroupRenderer)
"""

class FormRenderer(HTMLGenerator):
    def __init__(self, context:ContextualForm):
        self._context = context

    def draw(self):
        raise NotImplementedError("Subclasses must implement this method.")


class FieldsetRenderer(HTMLGenerator):
    def __init__(self, context:ContextualForm, fieldset:Fieldset.__class__):
        self._fieldset = fieldset
        self._context = context

    def draw(self):
        raise NotImplementedError("Subclasses must implement this method.")

class GroupRenderer(HTMLGenerator):
    def __init__(self, context:ContextualForm, group:FormGroup):
        self._context = context
        self._group = group

    def draw(self):
        raise NotImplementedError("Subclasses must implement this method.")

class FieldRenderer(HTMLGenerator):
    def __init__(self, context:ContextualForm, field:FormField):
        self._context = context
        self._field = field

    def draw(self):
        raise NotImplementedError("Subclasses must implement this method.")


class FormControlRenderer(HTMLGenerator):
    def __init__(self, context:ContextualForm, field:FormField):
        self._context = context
        self._field = field

    def draw(self):
        raise NotImplementedError("Subclasses must implement this method.")


###################################################
## Default implementations

class DefaultFormRenderer(FormRenderer):
    def draw(self):
        ctx = self._context.struct.ref_
        data = self._context.data

        fieldsets = ctx.fieldsets
        fieldset_frags = []
        for fieldset in fieldsets:
            r = fieldset.get_renderer(ctx)
            fieldset_frags.append(r.draw())
        fieldsets_frag = "\n" + "\n".join(fieldset_frags) + "\n"

        html = self._make_tag('form',
                       content=fieldsets_frag,
                       attributes={
                          "id": ctx.name + "_form",
                          "action": ctx.action,
                          "method": ctx.method
                       }
                    )

        return html


class DefaultFieldsetRenderer(FieldsetRenderer):
    def draw(self):
        fs = self._fieldset

        fields = self._context.get_fieldset_fields(fs)
        field_frags = []
        for field in fields:
            r = None
            if isinstance(field, FormField):
                r = field.get_field_renderer(self._context)
            elif isinstance(field, FormGroup):
                r = field.ref_.get_renderer(self._context)
            if r is not None:
                field_frags.append(r.draw())

        fields_frag = "\n" + "\n".join(field_frags) + "\n"

        html = self._make_tag('fieldset',
                              content=fields_frag,
                              attributes={
                                  "id": fs.name + "_fieldset",
                              }
                            )

        return html

class DefaultGroupRenderer(GroupRenderer):
    def draw(self):
        fields = self._group.ref_.all
        frag = []
        for field in fields:
            if isinstance(field, FormField):
                r = field.get_field_renderer(self._context)
                frag.append(r.draw())
            elif isinstance(field, FormGroup):
                r = field.ref_.get_renderer(self._context)
                frag.append(r.draw())
        group_frag = "\n".join(frag)
        return group_frag

class DefaultFieldRenderer(FieldRenderer):
    def draw(self):
        control_renderer = self._field.get_control_renderer(self._context)
        field_frag = control_renderer.draw()
        field_frag = "\n" + field_frag + "\n"
        html = self._make_tag("div", content=field_frag)
        return html


class DefaultFormControlRenderer(FormControlRenderer):
    def draw(self):
        control = self._field.get_control()
        field_frag = control.draw()
        field_frag = "\n" + field_frag + "\n"
        html = self._make_tag("div", content=field_frag)
        return html




