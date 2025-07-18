from formulaic.core import ErrorCode


class ValueNotInAllowedList(ErrorCode): id="value_not_in_allowed_list"
class ValueNotInAllowedRange(ErrorCode): id="value_not_in_allowed_range"
class NoneNotAllowed(ErrorCode): id="none_not_allowed"
class ListNotFound(ErrorCode): id="list_not_found"
class EmptyArrayNotPermitted(ErrorCode): id="empty_array_not_permitted"
class Required(ErrorCode): id="required"
class FieldNotInAllowedList(ErrorCode): id="field_not_in_allowed_list"