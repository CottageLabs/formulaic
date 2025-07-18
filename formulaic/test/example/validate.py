from formulaic.core import Validator

class IsISSN(Validator):
    def validate(self, val, field):
        if len(val) > 9 or val == '':
            raise ValueError("Unable to normalise {x} to valid ISSN".format(x=issn))

        # TODOL apply ISSN regex