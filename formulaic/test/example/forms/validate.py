#####################################
## DOAJ-specific validators
from formulaic.validate.validate import RequiredValue


class RequiredValueDOAJ(RequiredValue):
    def html_attrs(self, attrs):
        attrs["data-parsley-requiredvalue"] = self.required_value