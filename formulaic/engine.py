from copy import deepcopy
from typing import Union

from formulaic.core import Field, Structure, CoerceError, ValidationError, DataProcessingResult, StructureError, StructRef
from formulaic.error_codes import ValueNotInAllowedList, NoneNotAllowed, ListNotFound, \
    EmptyArrayNotPermitted, Required, FieldNotInAllowedList
from formulaic.lib import unity

################################################
## Data retrieval

def get_data(reference: Union[Field, Structure, StructRef], data: dict, default=None, by_reference=True):
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
        return get_single(reference, data, default=default, by_reference=by_reference)

    else:
        return get_list(reference, data, default=default, by_reference=by_reference)


def get_single(reference: Union[Field, Structure, StructRef], data: dict, default=None, by_reference=True):
    """
    Retrieve a single value field from the data structure.

    In reality, this is a general purpose function that can retrieve any value, but it does not apply special
    handling for lists.

    :param reference:
    :param data:
    :param default:
    :param by_reference:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    val = _get_path(reference, data, default=default)

    if not by_reference:
        val = deepcopy(val)

    return val


def get_list(reference: Union[Field, Structure, StructRef], data: dict, default=None, by_reference=True):
    """
    Retrieve a list from the data structure.

    If the list does not exist and by_reference is requested, it will be created, otherwise you will get an empty list
    (or your default if provided).
    :param reference:
    :param data:
    :param default:
    :param by_reference:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    if default is None:
        default = []

    if not isinstance(default, list):
        default = [default]

    values = _get_path(reference, data)

    # if there is no value and we want to do by reference, then create it, bind it and return it
    if values is None and by_reference:
        mylist = default
        return set_list(reference, mylist, data, force_accept_empty=True)

    # otherwise, default is an empty list
    elif values is None and not by_reference:
        return default

    # check that the val is actually a list
    if not isinstance(values, list):
        s = StructureError(reference, values, ListNotFound())
        raise DataProcessingResult(errors=[s])

    if by_reference:
        return values
    return deepcopy(values)


def exists_in_list(reference: Union[Field, Structure, StructRef], data: dict, value=None, matchsub=None, apply_structure_on_matchsub=True):
    """
    Check if a value or partial dictionary exists in a list.

    In the case of a value, we check to see if the value as-is appears in the list

    In the case of the partial dictionary (matchsub), we check to see if there is at least one entry in the list which
    matches all the keys and values in the matchsub dictionary.

    You may only supply one of `value` or `matchsub`. If both are provided, a ValueError is raised.

    :param reference:
    :param data:
    :param value:
    :param matchsub:
    :param apply_structure_on_matchsub:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    if value is not None and matchsub is not None:
        raise ValueError("Cannot check existence in list with both `value` and `matchsub` provided. Use one or the other.")

    if value is None and matchsub is None:
        raise ValueError("Must provide either `value` or `matchsub` to check existence in list.")

    current = get_list(reference, data, by_reference=True)

    if value is not None:
        if value in current:
            return True
        return False

    # if we get to here, we are comparing with the matchsub

    if apply_structure_on_matchsub:
        if isinstance(reference, Field):
             raise ValueError("Cannot apply structure on matchsub when checking a Field. Use a Structure instead.")
        matchsub = apply_structure(reference.struct, matchsub, required_check=False, silent_prune=False, allow_other_fields=True)

    for entry in current:
        matches = 0
        for k, v in matchsub.items():
            if entry.get(k) == v:
                matches += 1
        if matches == len(list(matchsub.keys())):
            return True

    return False


##############################################
## Data setting

def set_data(reference: Union[Field, Structure, StructRef], value, data: dict, required_check=True, silent_prune=False, allow_other_fields=False):
    """
    Set the value in the data dictionary at the path specified by the reference.  This will delegate to the appropriate
    method for handling single values or lists based on the repeatability of the reference.

    :param reference:
    :param value:
    :param data:
    :param required_check:
    :param silent_prune:
    :param allow_other_fields:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    if not reference.repeatable:
        return set_single(reference, value, data, required_check=required_check, silent_prune=silent_prune, allow_other_fields=allow_other_fields)

    else:
        return set_list(reference, value, data, required_check=required_check, silent_prune=silent_prune, allow_other_fields=allow_other_fields)


def set_single(reference: Union[Field, Structure, StructRef], value, data: dict, required_check=True, silent_prune=True, allow_other_fields=False):
    """
    Set the given value in the data dictionary at the path specified by the reference.

    This works generically for Fields and Structures, but does not handle lists.  Use `set_list` for that.
    :param reference:
    :param value:
    :param data:
    :param required_check:
    :param silent_prune:
    :param allow_other_fields:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    if reference.repeatable:
        raise ValueError("Cannot set a single value on a repeatable reference. Use set_list instead.")

    if isinstance(reference, Field):
        if value is None and reference.ignore_none:
            return None
        value = apply_field_constraints(reference, value, data)

    elif isinstance(reference, StructRef):
        value = apply_structure(reference.struct, value, required_check=required_check, silent_prune=silent_prune, allow_other_fields=allow_other_fields)

    return _set_path(reference, value, data)


def set_list(reference: Union[Field, Structure, StructRef], value, data: dict, required_check=True, silent_prune=True, allow_other_fields=False, force_accept_empty=False):
    """
    Set the given value in the data dictionary at the path specified by the reference.  If the value is not a list, it
    will be converted into a single element list.

    All list elements will be coerced and structured according to the reference's requirements

    :param reference:
    :param value:
    :param data:
    :param required_check:
    :param silent_prune:
    :param allow_other_fields:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    if not isinstance(value, list):
        value = [value]

    coerced = []
    validation_result = DataProcessingResult()

    for v in value:
        if value is None and reference.ignore_none:
            continue

        try:
            if isinstance(reference, StructRef):
                # if we are dealing with a StructRef, we need to apply the structure to the value
                v = apply_structure(reference.struct, v, required_check=required_check, silent_prune=silent_prune, allow_other_fields=allow_other_fields)
            else:
                v = apply_field_constraints(reference, v, data)
        except DataProcessingResult as dpr:
            # if we get a DataProcessingResult, we need to add the errors to the validation result
            validation_result.merge(dpr)
            continue

        coerced.append(v)

    if not validation_result.is_valid:
        raise validation_result

    # check that the cleaned array isn't empty
    if len(coerced) == 0 and not force_accept_empty:
        # this is equivalent to a None, so we need to decide what to do
        if reference.ignore_none:
            # if we are ignoring nones, just do nothing
            return None
        elif not reference.allow_none:
            e = ValidationError(reference, None, EmptyArrayNotPermitted())
            raise DataProcessingResult(errors=[e])

    return _set_path(reference, coerced, data)


def add_to_list(reference: Union[Field, Structure, StructRef], value, data: dict, required_check=True, silent_prune=True, allow_other_fields=False):
    """
    Add the given value to the list at the path specified by the reference.

    This can handle both single values and structures

    :param reference:
    :param value:
    :param data:
    :param required_check:
    :param silent_prune:
    :param allow_other_fields:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    if value is None and reference.ignore_none:
        return None

    if isinstance(reference, StructRef):
        # if we are dealing with a StructRef, we need to apply the structure to the value
        value = apply_structure(reference.struct, value, required_check=required_check, silent_prune=silent_prune, allow_other_fields=allow_other_fields)
    else:
        value = apply_field_constraints(reference, value, data)

    current = get_list(reference, data, by_reference=True)

    if reference.unique:
        if value in current:
            # if the value is already in the list, we do not add it again
            return value

    current.append(value)
    return value

###############################################
## Data removal

def delete_data(reference: Union[Field, Structure, StructRef], data: dict, prune=True):
    if isinstance(reference, Structure):
        reference = reference._ref

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


def delete_from_list(reference: Union[Field, Structure, StructRef], data: dict, val=None, matchsub=None, prune=True, apply_structure_on_matchsub=True):
    """
    Note that matchsub will be coerced with the struct if it exists, to ensure
    that the match is done correctly

    :param path:
    :param val:
    :param matchsub:
    :param prune:
    :return:
    """
    if isinstance(reference, Structure):
        reference = reference._ref

    l = get_list(reference, data, by_reference=True)

    removes = []
    for i, entry in enumerate(l):
        if val is not None:
            if entry == val:
                removes.append(i)
        elif matchsub is not None:
            if apply_structure_on_matchsub:
                if isinstance(reference, Field):
                    raise ValueError(
                        "Cannot apply structure on matchsub when checking a Field. Use a Structure instead.")
                matchsub = apply_structure(reference.struct, matchsub, required_check=False, silent_prune=False,
                                           allow_other_fields=True)
            matches = 0
            for k, v in matchsub.items():
                if entry.get(k) == v:
                    matches += 1
            if matches == len(list(matchsub.keys())):
                removes.append(i)

    removes.sort(reverse=True)
    for r in removes:
        del l[r]

    if len(l) == 0 and prune:
        delete_data(reference, data, prune=prune)

###################################################
## Sturcture wide capabilities

def apply_field_constraints(reference: Field, value, data):
    if value is None and not reference.allow_none:
        e = ValidationError(reference, None, NoneNotAllowed())
        raise DataProcessingResult(errors=[e])

    value = _do_coerce(value, reference)
    if isinstance(value, CoerceError):
        raise DataProcessingResult(errors=[value])

    valid = _do_validate(value, reference, data)
    if isinstance(valid, ValidationError):
        raise DataProcessingResult(errors=[valid])

    return value

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
            if unity.name(r) not in keyset:
                dpr.add_error(ValidationError(r, None, Required(), path=unity.path(r)))

        for s in structure._ref.structures:
            nd = data.get(s._name, None)
            if nd is not None:
                if s._ref.repeatable:
                    entries = data.get(s._name, [])
                    if not isinstance(entries, list):
                        entries = [entries]
                    for e in entries:
                        recurse(s, e, dpr)
                else:
                    recurse(s, data.get(s._name, {}), dpr)

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
                    dpr.add_error(ValidationError(structure, None, FieldNotInAllowedList(), subfield=k))

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
                    v = apply_field_constraints(field, v, data)
                    nvals.append(v)
                constructed[field.name] = nvals  # update the data dict with the coerced values
            else:
                val = apply_field_constraints(field, val, data)
                constructed[field.name] = val  # update the data dict with the coerced value

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

    ready = recurse(structure, data, dpr)

    # if we are checking required fields, then check them
    if required_check:
        try:
            check_required(structure, ready)
        except DataProcessingResult as sdpr:
            dpr.merge(sdpr)

    return ready

# def validate(reference: Union[Field, Structure, StructRef], data: dict):
#
#     def recurse(struct, context):
#         # check that only the allowed keys are present
#         keys = struct.raw.keys()
#         for k in keys:
#             if k not in ["fields", "objects", "lists", "required", "structs"]:
#                 raise SeamlessException("Key '{x}' present in struct at '{y}', but is not permitted".format(x=k, y=context))
#
#         # now go through and make sure the fields are the right shape:
#         for field_name, instructions in struct.fields:
#             for k,v in instructions.items():
#                 if not isinstance(v, list) and not isinstance(v, str) and not isinstance(v, bool):
#                     raise SeamlessException("Argument '{a}' in field '{b}' at '{c}' is not a string, list or boolean".format(a=k, b=field_name, c=context))
#
#         # then make sure the objects are ok
#         for o in struct.objects:
#             if not isinstance(o, str):
#                 raise SeamlessException("There is a non-string value in the object list at '{y}'".format(y=context))
#
#         # make sure the lists are correct
#         for field_name, instructions in struct.lists:
#             contains = instructions.get("contains")
#             if contains is None:
#                 raise SeamlessException("No 'contains' argument in list definition for field '{x}' at '{y}'".format(x=field_name, y=context))
#             if contains not in ["object", "field"]:
#                 raise SeamlessException("'contains' argument in list '{x}' at '{y}' contains illegal value '{z}'".format(x=field_name, y=context, z=contains))
#             for k,v in instructions.items():
#                 if not isinstance(v, list) and not isinstance(v, str) and not isinstance(v, bool):
#                     raise SeamlessException("Argument '{a}' in list '{b}' at '{c}' is not a string, list or boolean".format(a=k, b=field_name, c=context))
#
#         # make sure the requireds are correct
#         for o in struct.required:
#             if not isinstance(o, str):
#                 raise SeamlessException("There is a non-string value in the required list at '{y}'".format(y=context))
#
#         # now do the structs, which will involve some recursion
#         substructs = struct.substructs
#
#         # first check that there are no previously unknown keys in there
#         possibles = struct.objects + list(struct.list_names)
#         for s in substructs:
#             if s not in possibles:
#                 raise SeamlessException("struct contains key '{a}' which is not listed in object or list definitions at '{x}'".format(a=s, x=context))
#
#         # now recurse into each struct
#         for k, v in substructs.items():
#             nc = context
#             if nc == "":
#                 nc = k
#             else:
#                 nc += "." + k
#             recurse(Construct(v, None, None), context=nc)
#
#         return True
#
#     recurse(self, "[root]")

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


def _do_validate(value, reference: Field, data: dict):
    validators = reference.validators
    if validators is None or len(validators) == 0:
        return True

    if len(reference.allowed_values) > 0:
        if value not in reference.allowed_values:
            return ValidationError(reference, value, ValueNotInAllowedList(), allowed_values=reference.allowed_values)

    if reference.has_allowed_range():
        lower, upper = reference.allowed_range
        if (lower is not None and value < lower) or (upper is not None and value > upper):
            return ValidationError(reference, value, ValueNotInAllowedList(), allowed_range=reference.allowed_range)

    for validator in validators:
        result = validator.validate(value, reference, data)
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


def _set_path(reference: Union[Field, StructRef], value, data: dict):
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

def _prune_stack(stack):
    while len(stack) > 0:
        context = stack.pop()
        todelete = []
        for k, v in context.items():
            if isinstance(v, dict) and len(list(v.keys())) == 0:
                todelete.append(k)
        for d in todelete:
            del context[d]