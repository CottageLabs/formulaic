from copy import deepcopy

from formulaic.forms.core import HTMLGenerator


class FormControl(HTMLGenerator):
    def __init__(self, owner):
        self._owner = owner

    def inputs_and_labels(self, kvs=None) -> list[dict]:
        raise NotImplementedError("Subclasses must implement this method.")

    def draw(self, kvs=None):
        inputs_and_labels = self.inputs_and_labels(kvs)

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
        attrs["id"] = name

        disabled = self._owner.disabled
        if disabled:
            attrs['disabled'] = 'disabled'

        self._owner.validators = self._owner.validators or []
        for validator in self._owner.validators:
            validator.html_attrs(attrs)

        return attrs

    def _id(self, namespace, field_name, field_value):
        pass

#########################################################
# Form Controls

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


class TextInput(FormControl):
    def inputs_and_labels(self, prefix=None, values=None):
        attrs = self._generic_attributes()
        attrs["type"] = "text"

        label = self._owner.label or ""
        placeholder = self._owner.placeholder or ""
        attrs["placeholder"] = placeholder

        if kvs is None:
            input_tag = self._make_tag('input', attributes=attrs, close=False)
            label_tag = self._make_tag('label', attributes={"for": attrs["id"]}, content=label)
            tags = [{"control": input_tag, "label": label_tag}]

        else:
            tags = []
            for k, v in kvs.items():
                item_attrs = deepcopy(attrs)
                item_attrs["name"] = k
                item_attrs["id"] = k
                item_attrs["value"] = v or ""

                input_tag = self._make_tag('input', attributes=item_attrs, close=False)
                label_tag = self._make_tag('label', attributes={"for": item_attrs["id"]}, content=label)
                tags.append({"control": input_tag, "label": label_tag})

        return tags


class NumberInput(FormControl):
    def inputs_and_labels(self, kvs=None):
        attrs = self._generic_attributes()
        attrs["type"] = "number"

        id = f"{self._owner.name}_input"
        attrs["id"] = id

        input_tag = self._make_tag('input', attributes=attrs, close=False)

        label = self._owner.label or ""
        label_tag = self._make_tag('label', attributes={"for": id}, content=label)
        tags = [{"control": input_tag, "label": label_tag}]

        return tags


class Select(FormControl):
    def inputs_and_labels(self, kvs=None):
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
