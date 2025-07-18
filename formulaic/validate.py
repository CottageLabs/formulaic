from urllib.parse import urlparse

from formulaic.core import Validator

class IsURL(Validator):
    def validate(self, val, field):
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