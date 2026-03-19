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