#####################################
## DOAJ-specific validators
from formulaic.core import Validator
from formulaic.validate.validate import RequiredValue


class RequiredValueDOAJ(RequiredValue):
    def html_attrs(self, attrs):
        attrs["data-parsley-requiredvalue"] = self.required_value

class JournalURLInPublicDOAJ(Validator):
    def validate(self, val, field, data):
        # Can't do this validator in test setup
        return True

class ISSNInPublicDOAJ(Validator):
    def validate(self, val, field, data):
        # Can't do this validator in test setup
        return True

class CurrentISOLanguage(Validator):
    def __init__(self, message=None):
        if not message:
            message = "Language is not in the currently supported ISO list"
        self.message = message
        super().__init__()

    def validate(self, val, field, data):
        return True
        # if field.data is not None and field.data != '':
        #     check = isolang.find(field.data)
        #     if check is None:
        #         raise validators.ValidationError(self.message)