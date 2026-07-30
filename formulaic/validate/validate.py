from typing import Union, Literal
from urllib.parse import urlparse
import re

from formulaic import engine
from formulaic.core import Validator, ValidationError, Field
from formulaic.error_codes import IsRequired, RegexDoesNotMatch, FieldsShouldBeDifferent, IsConditionallyRequired, \
    DisallowedValue, MultipleConnectedValidationFailures


class Required(Validator):
    """
    Determine if a field or structure is required to be present

    This validator can be explicitly added to the field or structure, but if not it will automatically
    be added to the object as a "binding validator", dependent on whether the structure is defined as
    REQUIRED when added to its parent
    """
    def validate(self, val, data, value_context):
        if isinstance(self._reference, Field) and val is None or val == "":
            return ValidationError(self._reference, val, IsRequired(self))
        elif val is None:
            return ValidationError(self._reference, val, IsRequired(self))
        return True


class Regex(Validator):
    """
    Validates the field against a user provided regex
    """
    def __init__(self, regex, reference=None, flags=0):
        if isinstance(regex, str):
            regex = re.compile(regex, flags)
        self._regex = regex

        super(Regex, self).__init__(reference)

    def validate(self, val, data, value_context):
        if val is None:
            return True

        match = self._regex.match(val or '')
        if not match:
            return ValidationError(self._reference, val, RegexDoesNotMatch(self))
        return True


class Different(Validator):
    def __init__(self, field1, field2, reference=None, ignore_empty=True):
        super(Different, self).__init__(reference)
        self._ignore_empty = ignore_empty
        self._field1 = field1
        self._field2 = field2
        # Cached once, never overwritten - see _bind_fields for why.
        self._field1_name = field1.name
        self._field2_name = field2.name

    def validate(self, val, data, value_context):
        self._bind_fields()
        f1_cval = engine.get_data__nested_list_aware(self._field1, data, value_context)
        f2_cval = engine.get_data__nested_list_aware(self._field2, data, value_context)

        f1_val = []
        f2_val = []
        if len(f1_cval) > 0:
            f1_val = [f[0] for f in f1_cval if not (self._ignore_empty and (f[0] == "" or f[0] is None))]
        if len(f2_cval) > 0:
            f2_val = [f[0] for f in f2_cval if not (self._ignore_empty and (f[0] == "" or f[0] is None))]
        f1_val.sort()
        f2_val.sort()

        if f1_val == f2_val:
            if self._ignore_empty and (len(f1_val) == 0 or len(f2_val) == 0):
                return True
            return ValidationError(self._reference, val,
                                   FieldsShouldBeDifferent(self, self._field1, self._field2),
                                   bind_to=[self._field1, self._field2])
        return True

    def _bind_fields(self):
        # Re-resolve from the cached original names, not from whatever the
        # previous call happened to leave in self._field1/self._field2. Struct
        # objects like TriageSubmission's are process-lifetime singletons
        # shared by every request, so these Validator instances are too -
        # resolving from self._fieldN.name would mean a single request where
        # by_name() returns None (e.g. a field not present in that request's
        # context) permanently breaks this validator for every request after
        # it, since None has no .name to re-resolve from on the next call.
        self._field1 = self._reference.ref_.by_name(self._field1_name)
        self._field2 = self._reference.ref_.by_name(self._field2_name)

class RequiredIfNot(Validator):
    def __init__(self, conditionally_required_field, depends_on_field, reference=None):
        super(RequiredIfNot, self).__init__(reference)
        self._conditionally_required_field = conditionally_required_field
        self._depends_on_field = depends_on_field
        # Cached once, never overwritten - see _bind_fields for why.
        self._conditionally_required_field_name = conditionally_required_field.name
        self._depends_on_field_name = depends_on_field.name

    def validate(self, val, data, value_context):
        self._bind_fields()
        cf_cval = engine.get_data__nested_list_aware(self._conditionally_required_field, data, value_context)
        df_cval = engine.get_data__nested_list_aware(self._depends_on_field, data, value_context)

        conditional_values = [f[0] for f in cf_cval if not (f[0] == "" or f[0] is None)]
        if len(conditional_values) > 0:
            # the conditionally required field has a value, so it is valid whatever
            return True

        raw_compare_to = [f[0] for f in df_cval if not (f[0] == "" or f[0] is None)]

        # we need to account for the possibility that the values at each object are also lists
        # so we unpack any nested lists
        compare_to = []
        for entry in raw_compare_to:
            if isinstance(entry, list):
                compare_to.extend(v for v in entry if v not in ("", None))
            else:
                compare_to.append(entry)

        if not compare_to:
            # if the depends_on_field has no value, then the conditionally_required_field is required
            return ValidationError(self._reference, val,
                                   IsConditionallyRequired(self),
                                   bind_to=self._conditionally_required_field)

        return True

    def _bind_fields(self):
        # See RequiredIf._bind_fields (same pattern) for why these resolve
        # from cached names rather than self._conditionally_required_field.name.
        self._conditionally_required_field = self._reference.ref_.by_name(self._conditionally_required_field_name)
        self._depends_on_field = self._reference.ref_.by_name(self._depends_on_field_name)

    def _match_single(self, compare_to):
        if isinstance(compare_to, list):
            return self._depends_on_value in compare_to
        else:
            return compare_to == self._depends_on_value

    def _match_list(self, compare_to):
        if isinstance(compare_to, list):
            return len(list(set(self._depends_on_value) & set(compare_to))) > 0
        else:
            return compare_to in self._depends_on_value

class RequiredIf(Validator):
    def __init__(self, conditionally_required_field, depends_on_field, depends_on_value, reference=None):
        super(RequiredIf, self).__init__(reference)
        self._conditionally_required_field = conditionally_required_field
        self._depends_on_field = depends_on_field
        self._depends_on_value = depends_on_value
        # Cached once, never overwritten - see _bind_fields for why.
        self._conditionally_required_field_name = conditionally_required_field.name
        self._depends_on_field_name = depends_on_field.name

    def validate(self, val, data, value_context):
        self._bind_fields()
        cf_cval = engine.get_data__nested_list_aware(self._conditionally_required_field, data, value_context)
        df_cval = engine.get_data__nested_list_aware(self._depends_on_field, data, value_context)

        conditional_values = [f[0] for f in cf_cval if not (f[0] == "" or f[0] is None)]
        if len(conditional_values) > 0:
            # the conditionally required field has a value, so it is valid whatever
            return True

        raw_compare_to = [f[0] for f in df_cval if not (f[0] == "" or f[0] is None)]

        # we need to account for the possibility that the values at each object are also lists
        # so we unpack any nested lists
        compare_to = []
        for entry in raw_compare_to:
            if isinstance(entry, list):
                compare_to.extend(v for v in entry if v not in ("", None))
            else:
                compare_to.append(entry)

        match = False
        if isinstance(self._depends_on_value, list):
            match = self._match_list(compare_to)
        else:
            match = self._match_single(compare_to)

        if match:
            # field is required and not set
            return ValidationError(self._reference, val,
                                   IsConditionallyRequired(self),
                                   bind_to=self._conditionally_required_field)
        return True

    def _bind_fields(self):
        # Struct objects (e.g. TriageSubmission.struct) are process-lifetime
        # singletons shared by every request, so this Validator instance is
        # too - resolving from self._fieldN.name instead of a separately
        # cached name would mean a single request where by_name() returns
        # None (e.g. a field not present in that request's context)
        # permanently breaks this validator for every request after it,
        # since None has no .name to re-resolve from on the next call.
        self._conditionally_required_field = self._reference.ref_.by_name(self._conditionally_required_field_name)
        self._depends_on_field = self._reference.ref_.by_name(self._depends_on_field_name)

    def _match_single(self, compare_to):
        if isinstance(compare_to, list):
            return self._depends_on_value in compare_to
        else:
            return compare_to == self._depends_on_value

    def _match_list(self, compare_to):
        if isinstance(compare_to, list):
            return len(list(set(self._depends_on_value) & set(compare_to))) > 0
        else:
            return compare_to in self._depends_on_value

class NoScriptTag(Validator):
    def validate(self, val, field, data):
        if val is not None and "<script>" in val:
            return ValidationError(self._reference, val, DisallowedValue(self, "{val}".format(val=val)))
        return True

class IsURL(Validator):
    def validate(self, val, data, value_context):
        if val is None:
            return True

        if not isinstance(val, str):
            return ValidationError(self._reference, val, DisallowedValue(self, "{val}".format(val=val)))

        val = val.strip()

        if val == '':
            return True

        # parse with urlparse
        url = urlparse(val)

        # now check the url has the minimum properties that we require
        if url.scheme and url.scheme.startswith("http"):
            return True
        else:
            return ValidationError(self._reference, val, RegexDoesNotMatch(self))

class RegexOnList(Validator):
    def __init__(self, regex, list_separator=",", flags=0, reference=None):
        if isinstance(regex, str):
            regex = re.compile(regex, flags)
        self._regex = regex
        self._list_separator = list_separator
        super(RegexOnList, self).__init__(reference)

    def validate(self, val, data, value_context):
        if not isinstance(val, str):
            return True

        vals = [v.strip() for v in val.split(self._list_separator) if v.strip() != ""]

        for v in vals:
            match = self._regex.match(v)
            if not match:
                return ValidationError(self._reference, val, RegexDoesNotMatch(self))

        return True

class AllInvalid(Validator):
    def __init__(self, *args, error_code=None, reference=None):
        self._validators = args
        self._error_code = error_code if error_code is not None else MultipleConnectedValidationFailures
        super(AllInvalid, self).__init__(reference)

    def validate(self, val, data, value_context):
        errors = []
        trips = 0
        for v in self._validators:
            v.bind(self._reference)
            result = v.validate(val, data, value_context)
            if result is not True:
                errors.append(result)
                trips += 1

        if trips == len(self._validators):
            refs = []
            for e in errors:
                refs += e.relevant_references
            return ValidationError(self._reference, val, self._error_code(self, errors), bind_to=refs)

        return True

#####################################################
## UNREVIEWED


class RequiredValue(Validator):
    def __init__(self, required_value):
        self.required_value = required_value

    def validate(self, val, field, data):
        if val != self.required_value:
            raise ValueError(f"Value '{val}' does not match the required value '{self.required_value}' for field '{field.name}'")

    def html_attrs(self, attrs):
        return {"data-required-value": self.required_value}


class OptionalIf(Validator):
    # A validator which makes a field optional if another field is set
    # and has a truthy value.
    # ~~OptionalIf:FormValidator~~

    def __init__(self, other_field_name, message=None, optvals=None, *args, **kwargs):
        self.other_field_name = other_field_name
        if not message:
            message = "This field is required in the current circumstances"
        self.message = message
        self.optvals = optvals if optvals is not None else []
        super(OptionalIf, self).__init__(*args, **kwargs)

    def validate(self, val, field, data):
        return True
        # TODO
    #     other_field = self.get_other_field(self.other_field_name, form)
    #
    #     # if no values (for other_field) which make this field optional
    #     # are specified...
    #     if not self.optvals:
    #         # ... just make this field optional if the other is truthy
    #         if bool(other_field.data):
    #             super(OptionalIf, self).__call__(form, field)
    #         else:
    #             # otherwise it is required
    #             dr = validators.DataRequired(self.message)
    #             dr(form, field)
    #     else:
    #         # if such values are specified, check for them
    #         no_optval_matched = True
    #         for v in self.optvals:
    #             if isinstance(other_field.data, list):
    #                 if v in other_field.data and len(other_field.data) == 1:
    #                     # must be the only option submitted - OK for
    #                     # radios and for checkboxes where a single
    #                     # checkbox, but no more, is required to make the
    #                     # field optional
    #                     no_optval_matched = False
    #                     self.__make_optional(form, field)
    #                     break
    #             if other_field.data == v:
    #                 no_optval_matched = False
    #                 self.__make_optional(form, field)
    #                 break
    #
    #         if no_optval_matched:
    #             if not field.data:
    #                 raise validators.StopValidation('This field is required')
    #
    # def __make_optional(self, form, field):
    #     super(OptionalIf, self).__call__(form, field)
    #     raise validators.StopValidation()

class StopWords(Validator):
    """
    ~~StopWords:FormValidator~~
    """
    def __init__(self, stopwords, message=None):
        super().__init__()
        self.stopwords = stopwords
        if not message:
            message = "You may not enter '{stop_word}' in this field"
        self.message = message

    def validate(self, val, field, data):
        for v in val:
            if v.strip() in self.stopwords:
                # raise validators.StopValidation(self.message.format(stop_word=v))
                raise ValueError(self.message.format(stop_word=v))

class MaxLen(Validator):
    """
    Maximum length validator. Works on anything which supports len(thing).

    Use {max_len} in your custom message to insert the maximum length you've
    specified into the message.

    ~~MaxLen:FormValidator~~
    """

    def __init__(self, max_len, message='Maximum {max_len}.', *args, **kwargs):
        self.max_len = max_len
        self.message = message
        super().__init__(*args, **kwargs)

    def validate(self, val, field, data):
        if len(field.data) > self.max_len:
            raise ValueError(self.message.format(max_len=self.max_len))

class OnlyIfExists(Validator):
    """
    Field only validates if other fields DOES have ANY values (or are truthy)
    ~~NotIf:FormValidator~~
    """
    def __init__(self):
        super().__init__()

    def validate(self, val, field, data):
        return True
        # others = self.get_other_fields(form)
        #
        # for o_f in self.other_fields:
        #     other = others[o_f["field"]]
        #     if not other.data or not field.data:
        #         validators.ValidationError(self.message)