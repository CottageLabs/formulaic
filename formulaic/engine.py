from copy import deepcopy
from typing import Union

from formulaic.core import Field, Structure, CoerceError, ValidationError, DataProcessingResult, StructureError, StructRef
from formulaic.error_codes import ValueNotInAllowedList, NoneNotAllowed, ListNotFound, CannotCoerceOutByReference, \
    EmptyArrayNotPermitted, Required, FieldNotInAllowedList
from formulaic.lib import unity

################################################
## Data retrieval

def get_data(reference: Union[Field, Structure, StructRef], data: dict, default=None, by_reference=True, coerce=True):
    """
    General entry point for retrieving data from a structure or field.

    :param reference:
    :param data:
    :param default:
    :param by_reference:
    :param coerce:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    if not reference.repeatable:
        return get_single(reference, data, default=default, by_reference=by_reference, coerce=coerce)

    else:
        return get_list(reference, data, default=default, by_reference=by_reference, coerce=coerce)


def get_single(reference: Union[Field, Structure, StructRef], data: dict, default=None, by_reference=True, coerce=True):
    if isinstance(reference, Structure):
        reference = reference._ref

    val = _get_path(reference, data, default=default)

    if isinstance(reference, Field):

        if coerce:
            val = _do_coerce(val, reference, dir="out")
            if isinstance(val, CoerceError):
                raise DataProcessingResult(errors=[val])

        if not by_reference:
            val = deepcopy(val)

    elif isinstance(reference, StructRef):
        if coerce:
            apply_structure(reference, val, required_check=False, silent_prune=True, allow_other_fields=True)

    return val


def get_list(reference: Union[Field, Structure], data: dict, default=None, by_reference=True, coerce=True):
    values = _get_path(reference, data)

    # if there is no value and we want to do by reference, then create it, bind it and return it
    if values is None and by_reference:
        mylist = []
        set_single(reference, mylist, data)
        return mylist

    # otherwise, default is an empty list
    elif values is None and not by_reference:
        return []

    # check that the val is actually a list
    if not isinstance(values, list):
        s = StructureError(reference, values, ListNotFound())
        raise DataProcessingResult(errors=[s])

    if by_reference:
        return values
    return deepcopy(values)


def exists_in_list(reference: Union[Field, Structure], data: dict, value=None, matchsub=None, apply_structure_on_matchsub=True):
    current = get_list(reference, data, by_reference=True, coerce=False)

    if value is not None:
        if value in current:
            return True
        return False

    if matchsub is None:
        raise ValueError("Either `value` or `matchsub` must be provided to check existence in list.")

    if apply_structure_on_matchsub:
        matchsub = apply_structure()

    for entry in current:
        # attempt to coerce the sub
        if apply_structure_on_matchsub:
            try:
                type, struct, instructions = self._struct.lookup(path)
                if struct is not None:
                    matchsub = struct.construct(matchsub, struct).data
            except:
                pass

        matches = 0
        for k, v in matchsub.items():
            if entry.get(k) == v:
                matches += 1
        if matches == len(list(matchsub.keys())):
            return True

    return False


##############################################
## Data setting

def set_data(reference: Union[Field, Structure], value, data: dict, required_check=True, silent_prune=False, allow_other_fields=False):
    if not reference.repeatable:
        return set_single(reference, value, data, required_check=required_check, silent_prune=silent_prune, allow_other_fields=allow_other_fields)

    elif reference.repeatable:
        return set_list(reference, value, data, check_required=check_required, silent_prune=silent_prune)

    else:
        raise Exception()


def set_single(reference: Union[Field, Structure], value, data: dict, required_check=True, silent_prune=True, allow_other_fields=False):
    if isinstance(reference, Field):
        if value is None and reference.ignore_none:
            return None
        value = apply_field_constraints(reference, value)
    elif isinstance(reference, Structure):
        value = apply_structure(reference, value, required_check=required_check, silent_prune=silent_prune, allow_other_fields=allow_other_fields)
    return _set_path(reference, value, data)


def apply_field_constraints(reference: Field, value):
    if value is None and not reference.allow_none:
        e = ValidationError(reference, None, NoneNotAllowed())
        raise DataProcessingResult(errors=[e])

    value = _do_coerce(value, reference, dir="in")
    if isinstance(value, CoerceError):
        raise DataProcessingResult(errors=[value])

    valid = _do_validate(value, reference)
    if isinstance(valid, ValidationError):
        raise DataProcessingResult(errors=[valid])

    return value


def set_list(reference: Field, value, data: dict):
    if not isinstance(value, list):
        value = [value]

    coerced = []
    validation_result = DataProcessingResult()

    for v in value:
        if value is None and reference.ignore_none:
            continue

        try:
            v = apply_field_constraints(reference, v)
        except DataProcessingResult as dpr:
            # if we get a DataProcessingResult, we need to add the errors to the validation result
            validation_result.merge(dpr)
            continue

        coerced.append(v)

    if not validation_result.is_valid:
        raise validation_result

    # check that the cleaned array isn't empty
    if len(coerced) == 0:
        # this is equivalent to a None, so we need to decide what to do
        if reference.ignore_none:
            # if we are ignoring nones, just do nothing
            return None
        elif not reference.allow_none:
            e = ValidationError(reference, None, EmptyArrayNotPermitted())
            raise DataProcessingResult(errors=[e])

    return _set_path(reference, coerced, data)


def add_to_list(reference: Field, value, data: dict):
    if value is None and reference.ignore_none:
        return None

    value = apply_field_constraints(reference, value)
    current = get_list(reference, data, by_reference=True, coerce=False)

    if reference.unique:
        if value in current:
            # if the value is already in the list, we do not add it again
            return value

    current.append(value)
    return value

###############################################
## Data removal

def delete_data(reference: Field, data: dict, prune=True):
    parts = reference.path
    context = data

    stack = []
    for i in range(len(parts)):
        p = parts[i]
        if p in context:
            if i < len(parts) - 1:
                stack.append(context[p])
                context = context[p]
            else:
                del context[p]
                if prune and len(stack) > 0:
                    stack.pop()  # the last element was just deleted
                    _prune_stack(stack)

def _prune_stack(stack):
    while len(stack) > 0:
        context = stack.pop()
        todelete = []
        for k, v in context.items():
            if isinstance(v, dict) and len(list(v.keys())) == 0:
                todelete.append(k)
        for d in todelete:
            del context[d]


###################################################
## Sturcture wide capabilities

def check_required(structure: Structure, data: dict):
    """
    Check that all required fields are present in the data according to the structure.
    """
    if data is None:
        return True

    dpr = DataProcessingResult()

    def recurse(structure: Structure, data: dict, dpr: DataProcessingResult):
        if data is None:
            return

        keyset = data.keys()
        required = structure._ref.all_required
        for r in required:
            if r._name not in keyset:
                dpr.add_error(ValidationError(r, None, Required(), field=unity.path(r)))

        for s in structure._ref.structures:
            nd = data.get(s._name, None)
            if nd is not None:
                return recurse(s, data.get(s._name, {}), dpr)

    recurse(structure, data, dpr)

    if not dpr.is_valid:
        raise dpr

    return True

def apply_structure(structure: Structure, data: dict, required_check=True, silent_prune=False, allow_other_fields=False):

    def recurse(structure: Structure, data: dict, dpr: DataProcessingResult = None):
        if data is None:
            return None
        # if not isinstance(obj, dict):
        #     raise SeamlessException("Expected a dict at '{c}' but found something else instead".format(c=context))

        keyset = data.keys()
        known = structure._ref.all_names

        # check that there are no fields that are not allowed
        # Note that since the construction mechanism copies fields explicitly, silent_prune just turns off this
        # check
        if not allow_other_fields and not silent_prune:
            for k in keyset:
                if k not in known:
                    dpr.add_error(ValidationError(structure, None, FieldNotInAllowedList(), field=k))

        # prepare to construct the new object
        constructed = {}

        for field in structure._ref.fields:
            if field.name not in data:
                continue

            val = data.get(field.name, None)
            if val is None and field.ignore_none:
                continue

            if field.repeatable:
                if not isinstance(val, list):
                    val = [val]
                nvals = []
                for v in val:
                    v = apply_field_constraints(field, v)
                    nvals.append(v)
                data[field.name] = nvals  # update the data dict with the coerced values
            else:
                val = apply_field_constraints(field, val)
                data[field.name] = val  # update the data dict with the coerced value

        for struct in structure._ref.structures:
            if struct._name not in data:
                continue

            val = data.get(struct._name, None)

            if struct._ref.repeatable:
                if not isinstance(val, list):
                    val = [val]

                nvals = []
                for v in val:
                    if type(val) != dict:
                        # raise SeamlessException("Expected dict at '{x}' but found '{y}'".format(x=struct._name, y=type(val)))
                        pass

                    v = recurse(struct, v, dpr=dpr)
                    nvals.append(v)

                constructed[struct._name] = nvals

            else:
                if type(val) != dict:
                    # raise SeamlessException("Expected dict at '{x}' but found '{y}'".format(x=struct._name, y=type(val)))
                    pass

                constructed[struct._name] = recurse(struct, val, dpr=dpr)

        # finally, if we allow other fields, make sure that they come across too
        if allow_other_fields:
            for k, v in data.items():
                if k not in known:
                    constructed[k] = v

        return constructed

    dpr = DataProcessingResult()

    # if we are checking required fields, then check them
    if required_check:
        try:
            check_required(structure, data)
        except DataProcessingResult as sdpr:
            dpr.merge(sdpr)

    ready = recurse(structure, data, dpr)
    return ready

###################################################
## essential utilities

def _do_coerce(value, reference: Field):
    cdef = reference.coerce
    if cdef is None or len(cdef) == 0:
        return value

    if not isinstance(cdef, list):
        cdef = [cdef]

    for cfo in cdef:
        if isinstance(cfo, type):
            cfo = cfo()
        result = cfo.coerce(value, reference)
        if isinstance(result, CoerceError):
            if reference.allow_coerce_failure:
                return value
            # the result is a CoerceError, which we should return (or throw)
            return result
        value = result

    return value


def _do_validate(value, reference: Field):
    validators = reference.validators
    if validators is None or len(validators) == 0:
        return True

    if len(reference.allowed_values) > 0:
        if value not in reference.allowed_values:
            return ValidationError(reference, value, ValueNotInAllowedList(), allowed_values=reference.allowed_values)

    if reference.allowed_range is not None:
        lower, upper = reference.allowed_range
        if (lower is not None and value < lower) or (upper is not None and value > upper):
            return ValidationError(reference, value, ValueNotInAllowedList(), allowed_range=reference.allowed_range)

    for validator in validators:
        result = validator.validate(value, reference)
        if isinstance(result, ValidationError):
            return result

    # if we make it here, everything is valid
    return True


def _get_path(reference: Union[Field, StructRef], data: dict, default=None):
    parts = reference.path
    context = data

    for i in range(len(parts)):
        p = parts[i]
        d = {} if i < len(parts) - 1 else default
        context = context.get(p, d)
    return context


def _set_path(reference: Field, value, data: dict):
    parts = reference.path
    context = data

    for i in range(len(parts)):
        p = parts[i]

        if p not in context and i < len(parts) - 1:
            context[p] = {}
            context = context[p]
        elif p in context and i < len(parts) - 1:
            context = context[p]
        else:
            context[p] = value

    return context[parts[-1]]