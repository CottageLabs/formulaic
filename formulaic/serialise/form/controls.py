from copy import deepcopy

from formulaic.serialise.form.core import FormFieldCapability, FormCapability, FieldsetCapability, \
    CompoundFieldCapability


class FormControl:
    def __init__(self, capability:FormFieldCapability):
        self._capability:FormFieldCapability = capability

    def inputs_and_labels(self, id_prefix, val, *args, **kwargs) -> list[dict]:
        raise NotImplementedError("Subclasses must implement this method.")

    def _generic_attributes(self):
        attrs = deepcopy(self._capability.attributes)
        if attrs is None:
            attrs = {}

        disabled = self._capability.disabled
        if disabled:
            attrs['disabled'] = 'disabled'

        required = False
        if isinstance(self._capability, FormFieldCapability):
            required = self._capability.field.required
        else:
            required = self._capability.struct.ref_.required

        if required:
            attrs["required"] = "required"

        # FIXME: validators need to be separated from their representations
        # in html
        validators = self._capability.field.validators or []
        for validator in validators:
            validator.html_attrs(attrs)

        return attrs

    # def _name(self):
    #     field = self._capability.field
    #     stack = field.stack
    #     if len(stack) < 2:
    #         raise Exception("Field must be inside a form at least")
    #
    #     root = stack.pop(0)
    #     field = stack.pop()
    #
    #     cap = root.ref_.get_capability(FormCapability)
    #     use_form_in_name = cap.use_form_in_name
    #     use_fieldsets_in_name = cap.use_fieldsets_in_name
    #     separator = cap.separator
    #
    #     ident = ""
    #     if use_form_in_name:
    #         ident = root.name_ + separator
    #
    #     for level in stack:
    #         if level.ref_.has_capability(FieldsetCapability):
    #             if use_fieldsets_in_name:
    #                 ident += level.name_ + separator
    #
    #         elif level.ref_.has_capability(CompoundFieldCapability):
    #             ident += level.name_ + separator
    #             if level.ref_.repeatable:
    #                 ident += "0" + separator
    #
    #     ident += field.name
    #     if field.repeatable:
    #         ident += separator + "0"
    #
    #     return ident


class Radio(FormControl):
    def inputs_and_labels(self, id_prefix, val, *args, **kwargs):
        attrs = self._generic_attributes()
        attrs["type"] = "radio"
        attrs["name"] = id_prefix

        tags = []

        form_cap = self._capability.field.root.ref_.get_capability(FormCapability)
        options = self._capability.get_options()
        for i, opt in enumerate(options):
            id = id_prefix + form_cap.separator + str(i)

            label = opt.get('label', '')
            label_attrs = {}
            label_attrs["for"] = id

            opt_value = opt.get('value', '')
            opt_attrs = deepcopy(attrs)
            opt_attrs['id'] = id
            opt_attrs['value'] = opt_value
            if opt_value == val:
                opt_attrs['checked'] = 'checked'

            tags.append({
                "label": {
                    "tag": "label",
                    "attrs": label_attrs,
                    "close": True,
                    "content": label
                },
                "control": {
                    "tag": "input",
                    "attrs": opt_attrs,
                    "close": False
                },
            })

        return tags

class BasicInput(FormControl):
    type = "text"

    def inputs_and_labels(self, id_prefix, val, *args, **kwargs):
        attrs = self._generic_attributes()
        attrs["type"] = self.type
        attrs["name"] = id_prefix
        attrs["id"] = id_prefix

        placeholder = self._capability.placeholder or ""
        attrs["placeholder"] = placeholder

        if val is not None:
            attrs["value"] = val

        label = self._capability.label or ""

        tags =[{
            "control": {
                "tag": "input",
                "attrs": attrs,
                "close": False,
            },
            "label": {
                "tag": "label",
                "attrs": {"for": attrs["id"]},
                "content": label
            }
        }]

        return tags

class TextInput(BasicInput):
    pass

class URLInput(BasicInput):
    type = "url"


class Select(FormControl):
    def inputs_and_labels(self, id_prefix, val, *args, **kwargs):
        attrs = self._generic_attributes()
        attrs["name"] = id_prefix
        attrs["id"] = id_prefix

        options = []

        placeholder = self._capability.placeholder
        default = self._capability.default or ""
        if placeholder:
            placeholder_attrs = {"value": default}
            if val == default or val is None:
                placeholder_attrs["selected"] = "selected"
            placeholder_option = {
                "tag": "option",
                "attrs": placeholder_attrs,
                "content": placeholder
            }
            options.append(placeholder_option)

        field_options = self._capability.get_options()
        for opt in field_options:
            value = opt.get('value', '')
            label = opt.get('label', '')
            option_attrs = {"value": value}
            if value == val:
                option_attrs["selected"] = "selected"
            option = {
                "tag": "option",
                "attrs": option_attrs,
                "content": label
            }
            options.append(option)

        select = {
            "tag": "select",
            "attrs": attrs,
            "content": options
        }

        label = self._capability.label or ""
        label_tag = {
            "tag": "label",
            "attrs": {"for": attrs["id"]},
            "content": label
        }

        tags = [{"control": select, "label": label_tag}]
        return tags

class Checkbox(FormControl):
    def inputs_and_labels(self, id_prefix, val, *args, **kwargs):
        attrs = self._generic_attributes()
        attrs["name"] = id_prefix
        attrs["type"] = "checkbox"
        form_cap = self._capability.field.root.ref_.get_capability(FormCapability)

        tags = []
        if not isinstance(val, list):
            val = [val]

        field_options = self._capability.get_options()
        for i, opt in enumerate(field_options):
            id = id_prefix + form_cap.separator + str(i)
            value = opt.get('value', '')

            option_attrs = deepcopy(attrs)
            option_attrs["id"] = id
            option_attrs["value"] = value
            if value in val:
                option_attrs["checked"] = "checked"

            option = {
                "tag": "input",
                "attrs": option_attrs
            }

            label = opt.get('label', '')
            label_tag = {
                "tag": "label",
                "attrs": {"for": option_attrs["id"]},
                "content": label
            }

            tags.append({"control": option, "label": label_tag})

        return tags

class NumberInput(FormControl):
    def inputs_and_labels(self, id_prefix, val, *args, **kwargs):
        attrs = self._generic_attributes()
        attrs["name"] = id_prefix
        attrs["id"] = id_prefix
        attrs["type"] = "number"

        if val is not None:
            attrs["value"] = val

        min = None
        max = None
        range = self._capability.field.allowed_range
        if len(range) == 1:
            min = range[0]
        elif len(range) == 2:
            min = range[0]
            max = range[1]

        if min is not None:
            try:
                min = int(min)
                attrs["min"] = min
            except:
                pass
        if max is not None:
            try:
                max = int(max)
                attrs["max"] = max
            except:
                pass

        input = {
            "tag": "input",
            "attrs": attrs,
            "close": False,
        }

        label = self._capability.label or ""
        label_tag = {
            "tag": "label",
            "attrs": {"for": attrs["id"]},
            "content": label
        }

        tags = [{"control": input, "label": label_tag}]
        return tags