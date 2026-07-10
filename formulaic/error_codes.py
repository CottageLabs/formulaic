from formulaic.core import ErrorCode


class IsRequired(ErrorCode):
    id="is_required"


class IsConditionallyRequired(ErrorCode):
    id="is_conditionally_required"

class DisallowedValue(ErrorCode):
    id="disallowed_value"

    def __init__(self, validator, disallowed_values=None):
        self.disallowed_values = disallowed_values if disallowed_values is not None else []
        if not isinstance(self.disallowed_values, list):
            self.disallowed_values = [self.disallowed_values]
        super().__init__(validator)

class ValueNotInAllowedList(ErrorCode):
    id="value_not_in_allowed_list"

    def __init__(self, validator, supplied_value, allowed_values):
        self.supplied_value = supplied_value
        self.allowed_values = allowed_values
        super().__init__(validator)

class ValueNotInAllowedRange(ErrorCode):
    id="value_not_in_allowed_range"

class NoneNotAllowed(ErrorCode):
    id="none_not_allowed"

class ListNotFound(ErrorCode):
    id="list_not_found"

class EmptyArrayNotPermitted(ErrorCode):
    id="empty_array_not_permitted"

class FieldNotInAllowedList(ErrorCode):
    id="field_not_in_allowed_list"

class RegexDoesNotMatch(ErrorCode):
    id="regex_not_match"

class FieldsShouldBeDifferent(ErrorCode):
    id="fields_should_be_different"

    def __init__(self, validator, field1, field2):
        self.field1 = field1
        self.field2 = field2
        super().__init__(validator)

class MultipleConnectedValidationFailures(ErrorCode):
    id = "multiple_connected_validation_errors"

    def __init__(self, validator, nested_errors):
        self.nested_errors = nested_errors
        super().__init__(validator)