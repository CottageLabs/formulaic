from formulaic.core import ErrorCode


class IsRequired(ErrorCode):
    id="is_required"


class ValueNotInAllowedList(ErrorCode):
    id="value_not_in_allowed_list"

    def __init__(self, supplied_value, allowed_values):
        self.supplied_value = supplied_value
        self.allowed_values = allowed_values
        super().__init__()

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