from copy import deepcopy

from formulaic.core import Field, Structure, OPTIONAL, SINGLE, UNIQUE, DUPLICABLE, StructRef
from typing import Union

from formulaic.lib import unity


class HTMLGenerator:
    def _make_tag(self, tag_name, attributes=None, close=True, content=None):
        """
        Create an HTML tag with the given name and attributes.
        """
        if content is None:
            content = ''

        attrs = ""
        if attributes is not None:
            attrs = ' '.join(f'{key}="{value}"' for key, value in attributes.items())
            attrs = " " + attrs if attrs else ""

        if close:
            return f'<{tag_name}{attrs}>{content}</{tag_name}>'
        else:
            return f'<{tag_name}{attrs} />'

# Form Controls
#####################################

class FormControl(HTMLGenerator):
    def __init__(self, owner):
        self._owner = owner

    def inputs_and_labels(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def draw(self):
        inputs_and_labels = self.inputs_and_labels()

        frag = ""
        for il in inputs_and_labels:
            control = il.get("control", "")
            label = il.get("label", "")
            frag += f"{label}\n{control}\n"

        return frag.strip()

    def _generic_attributes(self):
        attrs = self._owner.attributes
        if attrs is None:
            attrs = {}

        name = self._owner.name
        attrs['name'] = name

        disabled = self._owner.disabled
        if disabled:
            attrs['disabled'] = 'disabled'

        self._owner.validators = self._owner.validators or []
        for validator in self._owner.validators:
            validator.html_attrs(attrs)

        return attrs

    def _id(self, namespace, field_name, field_value):
        pass

class Radio(FormControl):
    def inputs_and_labels(self):
        attrs = self._generic_attributes()
        attrs["type"] = "radio"
        tags = []

        name = self._owner.name
        options = self._owner.get_options()
        for opt in options:
            label = opt.get('label', '')
            value = opt.get('value', '')
            id = f"{name}_{value}"
            opt_attrs = deepcopy(attrs)
            opt_attrs['id'] = id
            opt_attrs['value'] = value
            radio_tag = self._make_tag('input', attributes=opt_attrs, close=False)
            label_tag = self._make_tag('label', attributes={"for": id}, content=label)
            tags.append({"control": radio_tag, "label": label_tag})

        return tags

    def draw(self):
        inputs_and_labels = self.inputs_and_labels()

        frag = ""
        for il in inputs_and_labels:
            control = il.get("control", "")
            label = il.get("label", "")
            frag += f"{control}\n{label}\n"

        return frag.strip()

class TextInput(FormControl):
    def inputs_and_labels(self):
        attrs = self._generic_attributes()
        attrs["type"] = "text"

        label = self._owner.label or ""
        placeholder = self._owner.placeholder or ""
        attrs["placeholder"] = placeholder

        id = f"{self._owner.name}_input"
        attrs["id"] = id

        input_tag = self._make_tag('input', attributes=attrs, close=False)
        label_tag = self._make_tag('label', attributes={"for": id}, content=label)
        tags = [{"control": input_tag, "label": label_tag}]

        return tags

    def draw(self):
        return super(TextInput, self).draw()

class NumberInput(FormControl):
    def inputs_and_labels(self):
        attrs = self._generic_attributes()
        attrs["type"] = "number"

        id = f"{self._owner.name}_input"
        attrs["id"] = id

        input_tag = self._make_tag('input', attributes=attrs, close=False)

        label = self._owner.label or ""
        label_tag = self._make_tag('label', attributes={"for": id}, content=label)
        tags = [{"control": input_tag, "label": label_tag}]

        return tags

    def draw(self):
        return super(NumberInput, self).draw()

class Select(FormControl):
    def inputs_and_labels(self):
        attrs = self._generic_attributes()

        name = self._owner.name
        id = f"{name}_select"
        attrs["id"] = id

        placeholder = self._owner.placeholder
        default = self._owner.default or ""

        opt_tags = []
        if placeholder:
            placeholder_tag = self._make_tag('option', attributes={"value": default}, content=placeholder)
            opt_tags.append(placeholder_tag)

        options = self._owner.get_options()
        for opt in options:
            value = opt.get('value', '')
            label = opt.get('label', '')
            opt_attrs = {"value": value}
            option_tag = self._make_tag('option', attributes=opt_attrs, content=label)
            opt_tags.append(option_tag)

        opts_frag = "\n" + "\n".join(opt_tags) + "\n"
        select_tag = self._make_tag('select', attributes=attrs, content=opts_frag)

        label = self._owner.label or ""
        label_tag = self._make_tag('label', attributes={"for": id}, content=label)
        tags = [{"control": select_tag, "label": label_tag}]

        return tags

    def draw(self):
        return super(Select, self).draw()

# Field Field/Entry Renderers
######################################

class FormRenderer(HTMLGenerator):
    def __init__(self, context):
        self._context = context

    def draw(self):
        pass

class FieldsetRenderer(HTMLGenerator):
    def __init__(self, context, fieldset):
        self._fieldset = fieldset
        self._context = context

    def draw(self):
        pass

class FieldRenderer(HTMLGenerator):
    def __init__(self, context, field):
        self._context = context
        self._field = field

    def draw(self):
        pass

class FieldEntryRenderer(HTMLGenerator):
    def __init__(self, owner):
        self._owner = owner

    def draw(self):
        pass

class GroupRenderer(HTMLGenerator):
    def __init__(self, context, structure):
        self._context = context
        self._structure = structure

    def draw(self):
        pass


class GroupEntryRenderer(HTMLGenerator):
    def __init__(self, owner):
        self._owner = owner

    def draw(self):
        pass

######

class DefaultFormRenderer(FormRenderer):
    def draw(self):
        ctx = self._context

        fieldsets = ctx.fieldsets
        fieldset_frags = []
        for fs in fieldsets:
            r = fs.renderer(ctx, fs)
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
        for f in fields:
            r = None
            if isinstance(f, FormField):
                r = f.field_renderer(self._context, f)
            elif isinstance(f, FormGroup):
                r = f._form.group_renderer(self._context, f)
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

class DefaultFieldRenderer(FieldRenderer):
    def draw(self):
        control = self._field.get_control()
        field_frag = control.draw()
        field_frag = "\n" + field_frag + "\n"
        html = self._make_tag("div", content=field_frag)
        return html

class DefaultFieldEntryRenderer(FieldEntryRenderer):
    pass

class DefaultGroupRenderer(GroupRenderer):
    def draw(self):
        subs = self._structure._ref.all
        frag = []
        for sub in subs:
            if isinstance(sub, FormField):
                r = sub.field_renderer(self._context, sub)
                frag.append(r.draw())
            elif isinstance(sub, FormGroup):
                r = sub._form.group_renderer(self._context, sub)
                frag.append(r.draw())
        group_frag = "\n".join(frag)
        return group_frag

class DefaultGroupEntryRenderer(GroupEntryRenderer):
    pass

#######################################
## Form structures

class Fieldset:
    name = "_fieldset"
    label = "_label"
    renderer = DefaultFieldsetRenderer


# name = "_field"
# """Name of the field.  Subclasses should override this to provide a meaningful name."""
#
# # There is no coerce-in and coerce-out.  Our objective is to keep data in its correct form.  If you
# # want to convert that data, then you need to do that explicitly externally to this code, or
# # transform to another field which has the appropriate coercion.
#
# coerce = []
# """List of coercion classes to apply to the field value in order."""
#
# allow_coerce_failure = False
# """If True, then if coercion fails, the original value will be kept.  If False, then an error will be raised."""
#
# allowed_values = []
# """List of allowed values for the field.  If the value is not in this list, then an error will be raised.  Leave empty to allow any value."""
#
# allowed_range = ()
# """Tuple of two values representing the allowed range for the field value.  If the value is not in this range, then an error will be raised.  Leave empty to allow any value."""
#
# allow_none = True
# """If True, then None is allowed as a value for the field.  If False, then an error will be raised if None is set."""
#
# ignore_none = False
# """If True, then if the value is None, it will be ignored and not set.  If False, then None will be set as the value."""
#
# validators = []
# """List of validator classes to apply to the field value in order.  If any validator fails, an error will be raised."""

class FormField(Field):
    label = "_label"
    control = None
    options = []
    default = None
    placeholder = None
    js = []
    attributes = {}
    disabled = False
    multivalue = False
    repeatable = None
    conditional = False
    field_renderer = DefaultFieldRenderer
    entry_renderer = DefaultFieldEntryRenderer

    def __init__(self, need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=UNIQUE,
                 parent=None,
                 check_coherence=False,
                 fieldset=None,
                 fs_pos=0):
        """
        Initialize the field with its properties.

        :param need: Is the field required or optional? Use REQUIRED or OPTIONAL.
        :param multiplicity: Is the field single or repeatable? Use SINGLE or REPEATABLE.
        :param duplicability: Is the field unique or duplicable? Use UNIQUE or DUPLICABLE. Applies to repeatable fields only, ignored in other cases.
        :param parent: The containing Structure.  May be left as None, and will be populated when the structure is initialized.
        :param check_coherence: Should the properties of the field be checked for coherence? If True, then the field will check that the properties are coherent with each other.  Useful for testing, not recommended for general usage.
        """
        self._fieldset = fieldset
        self._fs_pos = fs_pos
        super(FormField, self).__init__(need=need, multiplicity=multiplicity, duplicability=duplicability, parent=parent, check_coherence=check_coherence)

    def get_options(self):
        if isinstance(self.options, list):
            return self.options
        elif callable(self.options):
            return self.options()
        return []

    def get_control(self):
        if self.control is None:
            raise ValueError("Field control not defined")
        return self.control(self)

    @property
    def fieldset(self):
        """
        Returns the fieldset associated with this field.
        """
        return self._fieldset

    @property
    def fs_pos(self):
        return self._fs_pos

    def clone(self):
        """
        Clone the field, returning a new instance with the same properties.
        """
        return self.__class__(need=self.need,
                              multiplicity=self.multiplicity,
                              duplicability=self.duplicability,
                              parent=self.parent,
                              fieldset=self.fieldset,
                              fs_pos=self.fs_pos)


class FormStructRef(StructRef):
    def __init__(self, struct: Union["Structure", "Structure.__class__"],
                 need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None,
                 fieldset=None,
                 fs_pos=0):
        self._fieldset = fieldset
        self._fs_pos = fs_pos

        super(FormStructRef, self).__init__(struct=struct,
                                            need=need,
                                            multiplicity=multiplicity,
                                            duplicability=duplicability,
                                            parent=parent)

    @property
    def fieldset(self):
        """
        Returns the fieldset associated with this structure reference.
        """
        return self._fieldset

    @property
    def fs_pos(self):
        return self._fs_pos

    def clone(self):
        """
        Clone the structure reference, returning a new instance with the same properties.
        """
        return self.struct.__class__(need=self.need,
                              multiplicity=self.multiplicity,
                              duplicability=self.duplicability,
                              parent=self.parent,
                              fieldset=self.fieldset,
                              fs_pos=self.fs_pos)

class FormGroup(Structure):
    _form = None
    _ref_class = FormStructRef

    def __init__(self, need=OPTIONAL,
                 multiplicity=SINGLE,
                 duplicability=DUPLICABLE,
                 parent=None,
                 fieldset=None,
                 fs_pos=0):
        super().__init__(need=need,
                         multiplicity=multiplicity,
                         duplicability=duplicability,
                         parent=parent,
                         fieldset=fieldset,
                         fs_pos=fs_pos)

class FormGroupInfo:
    label = "_label"
    js = []
    repeatable = None
    conditional = False
    group_renderer = DefaultGroupRenderer
    entry_renderer = DefaultGroupEntryRenderer


class FormContext:
    name = "_form_context"
    form: Structure = None
    renderer: FormRenderer = DefaultFormRenderer
    action = None
    method = "post"
    fieldset_ordering = []

    def draw(self):
        r = self.renderer(self)
        return r.draw()

    @property
    def fieldsets(self):
        known_fieldsets = set()
        subs = self.form._ref.all
        for sub in subs:
            fs = unity.get_prop(sub, "fieldset")
            known_fieldsets.add(fs)

        # assemble all fieldsets listed with ordering in the correct order
        ordered = []
        for fs in self.fieldset_ordering:
            if fs in known_fieldsets:
                ordered.append(fs)
                known_fieldsets.remove(fs)

        # all remaining fieldsets that were not ordered
        ordered.extend(known_fieldsets)

        return ordered

    def get_fieldset_fields(self, fieldset):
        subs = self.form._ref.all
        fields = []
        for sub in subs:
            fs = unity.get_prop(sub, "fieldset")
            if fs == fieldset:
                fields.append(sub)

        sorted_fields = sorted(fields, key=lambda f: unity.get_prop(f, "fs_pos") or 0)
        return sorted_fields