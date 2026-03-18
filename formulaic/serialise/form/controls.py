from copy import deepcopy

from formulaic.serialise.form.core import FormFieldCapability, FormCapability, FieldsetCapability, \
    CompoundFieldCapability


class FormControl:
    def __init__(self, capability:FormFieldCapability):
        self._capability:FormFieldCapability = capability

    def inputs_and_labels(self, form_kvs, *args, **kwargs) -> list[dict]:
        raise NotImplementedError("Subclasses must implement this method.")

    def _generic_attributes(self):
        attrs = self._capability.attributes
        if attrs is None:
            attrs = {}

        # FIXME: STILL WRONG, but closer
        name = self._name()
        attrs['name'] = name
        attrs["id"] = name

        disabled = self._capability.disabled
        if disabled:
            attrs['disabled'] = 'disabled'

        # FIXME: validators need to be separated from their representations
        # in html
        validators = self._capability.field.validators or []
        for validator in validators:
            validator.html_attrs(attrs)

        return attrs

    def _name(self):
        field = self._capability.field
        stack = field.stack
        if len(stack) < 2:
            raise Exception("Field must be inside a form at least")

        root = stack.pop(0)
        field = stack.pop()

        cap = root.ref_.get_capability(FormCapability)
        use_form_in_name = cap.use_form_in_name
        use_fieldsets_in_name = cap.use_fieldsets_in_name
        separator = cap.separator

        ident = ""
        if use_form_in_name:
            ident = root.name_ + separator

        for level in stack:
            if level.ref_.has_capability(FieldsetCapability):
                if use_fieldsets_in_name:
                    ident += level.name_ + separator

            elif level.ref_.has_capability(CompoundFieldCapability):
                ident += level.name_ + separator
                if level.repeatable:
                    ident += "0" + separator

        ident += field.name
        if field.repeatable:
            ident += separator + "0"

        return ident


class Radio(FormControl):
    def inputs_and_labels(self, form_kvs, *args, **kwargs):
        attrs = self._generic_attributes()
        name = attrs["name"]
        attrs["type"] = "radio"
        tags = []

        form_cap = self._capability.field.root.ref_.get_capability(FormCapability)
        options = self._capability.get_options()
        for i, opt in enumerate(options):
            id = name + form_cap.separator + str(i)

            label = opt.get('label', '')
            label_attrs = {}
            label_attrs["for"] = id

            value = opt.get('value', '')
            opt_attrs = deepcopy(attrs)
            opt_attrs['id'] = id
            opt_attrs['value'] = value

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