#####################################
## DOAJ-specific validators
from formulaic.validate.validate import RequiredValue


class RequiredValueDOAJ(RequiredValue):
    def html_attrs(self, attrs):
        attrs["data-parsley-requiredvalue"] = self.required_value

class JournalURLInPublicDOAJ(object):
    def validate(self, val, field, data):
        # Can't do this validator in test setup
        return True

class ISSNInPublicDOAJ(object):
    def validate(self, val, field, data):
        # Can't do this validator in test setup
        return True
