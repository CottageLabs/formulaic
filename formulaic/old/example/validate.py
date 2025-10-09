class ValidationError:
    def __init__(self, field, original_value, code, **kwargs):
        self.field = field
        self.original_value = original_value
        self.code = code
        self.params = kwargs

class ValidationResult:
    def __init__(self, errors=None):
        self.errors = errors if errors is not None else []

    def add_error(self, error):
        self.errors.append(error)

    def is_valid(self):
        return len(self.errors) == 0

class ValidationCode:
    id = "_id"

    def __init__(self, *args, **kwargs):
        pass

class Required(ValidationCode):
    id = "required"

class UUIDIncorrectLength(ValidationCode):
    id = "uuid_incorrect_length"

    def __init__(self, got, expected=32):
        super(UUIDIncorrectLength, self).__init__()
        self.got = got
        self.expected = expected

class Validator:
    def validate(self, val, field=None, formulaic_object=None):
        pass

class IsUUID(Validator):

    def __init__(self):
        pass

    def validate(self, val, field=None, formulaic_object=None):
        if len(val) != 32:
            return ValidationError(None, val, UUIDIncorrectLength(len(val)))