from urllib.parse import urlparse

from formulaic import engine
from formulaic.core import Validator

# FIXME: not sure if we need this yet
class Required(Validator):
    def validate(self, val, field, data):
        if val is None or val == "":
            raise ValueError("This field is required and cannot be empty.")

    def html_attrs(self, attrs):
        pass


class IsURL(Validator):
    HTTP_URL = (
        r'^(?:https?)://'  # Scheme: http(s) or ftp
        r'(?:[\w\-]+\.)*[\w\-]+'  # Domain name (optional subdomains)
        r'(?:\.[a-z]{2,})'  # Top-level domain (e.g., .com, .org)
        r'(?::(0|6[0-5][0-5][0-3][0-5]|[1-5][0-9][0-9][0-9][0-9]|[1-9][0-9]{0,3}))?'  # port (0-65535) preceded with `:`
        r'(?:\/[^\/\s]*)*'  # Path (optional)
        r'(?:\?[^\/\s]*)?'  # Query string (optional)
        r'(?:#[^\/\s]*)?$'  # Fragment (optional)
    )

    def validate(self, val, field, data):
        if not isinstance(val, str):
            raise ValueError("Argument passed to to_url was not a string, but type '{t}': '{val}'".format(t=type(val), val=val))

        val = val.strip()

        if val == '':
            return val

        # parse with urlparse
        url = urlparse(val)

        # now check the url has the minimum properties that we require
        if url.scheme and url.scheme.startswith("http"):
            return True
        else:
            raise ValueError("Could not convert string {val} to viable URL".format(val=val))

    def html_attrs(self, attrs):
        attrs["type"] = "url"
        attrs["pattern"] = self.HTTP_URL


class RequiredValue(Validator):
    def __init__(self, required_value):
        self.required_value = required_value

    def validate(self, val, field, data):
        if val != self.required_value:
            raise ValueError(f"Value '{val}' does not match the required value '{self.required_value}' for field '{field.name}'")

    def html_attrs(self, attrs):
        return {"data-required-value": self.required_value}

class RequiredIf(Validator):
    def __init__(self, other_field_path, other_value):
        self.other_field_path = other_field_path
        self.other_value = other_value

    def validate(self, val, field, data):
        root = field.root
        other_field = root.get_path(self.other_field_path)
        compare_to = engine.get_data(other_field, data)

        if isinstance(self.other_value, list):
            self._match_list(val, compare_to)
        else:
            self._match_single(val, compare_to)

    def _match_single(self, val, compare_to):
        if isinstance(compare_to, list):
            match = self.other_value in compare_to
        else:
            match = compare_to == self.other_value

        if match and val is None:
            # field is required and not set
            raise ValueError("Field is required because other field matches the required value.")

        return True

    def _match_list(self, val, compare_to):
        if isinstance(compare_to, list):
            match = len(list(set(self.other_value) & set(compare_to))) > 0
        else:
            match = compare_to in self.other_value

        if match and val is None:
            # field is required and not set
            raise ValueError("Field is required because other field matches the required value.")

        return True

class NoScriptTag(Validator):
    def validate(self, val, field, data):
        if val is not None and "<script>" in val:
            raise ValueError(self.message)

class OptionalIf(Validator):
    # A validator which makes a field optional if another field is set
    # and has a truthy value.
    # ~~OptionalIf:FormValidator~~

    def __init__(self, other_field_name, message=None, optvals=None, *args, **kwargs):
        self.other_field_name = other_field_name
        if not message:
            message = "This field is required in the current circumstances"
        self.message = message
        self.optvals = optvals if optvals is not None else []
        super(OptionalIf, self).__init__(*args, **kwargs)

    def validate(self, val, field, data):
        return True
        # TODO
    #     other_field = self.get_other_field(self.other_field_name, form)
    #
    #     # if no values (for other_field) which make this field optional
    #     # are specified...
    #     if not self.optvals:
    #         # ... just make this field optional if the other is truthy
    #         if bool(other_field.data):
    #             super(OptionalIf, self).__call__(form, field)
    #         else:
    #             # otherwise it is required
    #             dr = validators.DataRequired(self.message)
    #             dr(form, field)
    #     else:
    #         # if such values are specified, check for them
    #         no_optval_matched = True
    #         for v in self.optvals:
    #             if isinstance(other_field.data, list):
    #                 if v in other_field.data and len(other_field.data) == 1:
    #                     # must be the only option submitted - OK for
    #                     # radios and for checkboxes where a single
    #                     # checkbox, but no more, is required to make the
    #                     # field optional
    #                     no_optval_matched = False
    #                     self.__make_optional(form, field)
    #                     break
    #             if other_field.data == v:
    #                 no_optval_matched = False
    #                 self.__make_optional(form, field)
    #                 break
    #
    #         if no_optval_matched:
    #             if not field.data:
    #                 raise validators.StopValidation('This field is required')
    #
    # def __make_optional(self, form, field):
    #     super(OptionalIf, self).__call__(form, field)
    #     raise validators.StopValidation()

class DifferentTo(Validator):
    """
    ~~DifferentTo:FormValidator~~
    """
    def __init__(self, other_field_name, ignore_empty=True, message=None):
        super(DifferentTo, self).__init__()
        self.ignore_empty = ignore_empty
        # if not message:
        #     message = "This field must contain a different value to the field '{x}'".format(x=self.other_field_name)
        self.message = message

    def validate(self, val, field, data):
        return True
        # TODO
        # other_field = self.get_other_field(self.other_field_name, form)
        #
        # if other_field.data == field.data:
        #     if self.ignore_empty and (not other_field.data or not field.data):
        #         return
        #     raise validators.ValidationError(self.message)

class StopWords(Validator):
    """
    ~~StopWords:FormValidator~~
    """
    def __init__(self, stopwords, message=None):
        super().__init__()
        self.stopwords = stopwords
        if not message:
            message = "You may not enter '{stop_word}' in this field"
        self.message = message

    def validate(self, val, field, data):
        for v in val:
            if v.strip() in self.stopwords:
                # raise validators.StopValidation(self.message.format(stop_word=v))
                raise ValueError(self.message.format(stop_word=v))

class MaxLen(Validator):
    """
    Maximum length validator. Works on anything which supports len(thing).

    Use {max_len} in your custom message to insert the maximum length you've
    specified into the message.

    ~~MaxLen:FormValidator~~
    """

    def __init__(self, max_len, message='Maximum {max_len}.', *args, **kwargs):
        self.max_len = max_len
        self.message = message
        super().__init__(*args, **kwargs)

    def validate(self, val, field, data):
        if len(field.data) > self.max_len:
            raise ValueError(self.message.format(max_len=self.max_len))
