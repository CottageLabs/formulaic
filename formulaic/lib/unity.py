from __future__ import annotations
from typing import Union

def is_required(f: Union["Field", "Structure"]) -> bool:
    from formulaic.core import Field, Structure

    return (isinstance(f, Field) and f.required) or (isinstance(f, Structure) and f.ref_.required)


def path(f: Union["Field", "Structure"]) -> str:
    from formulaic.core import Field, Structure

    if isinstance(f, Field):
        return f.path
    elif isinstance(f, Structure):
        return f.ref_.path
    else:
        raise TypeError("Expected Field or Structure instance.")


def name(f: Union["Field", "Structure"]) -> str:
    from formulaic.core import Field, Structure

    if isinstance(f, Field):
        return f.name
    elif isinstance(f, Structure):
        return f.name_
    else:
        raise TypeError("Expected Field or Structure instance.")


def clone(f: Union["Field", "Structure"]) -> Union["Field", "Structure"]:
    from formulaic.core import Field, Structure

    if isinstance(f, Field):
        return f.clone()
    elif isinstance(f, Structure):
        return f.ref_.clone()
    else:
        raise TypeError("Expected Field or Structure instance.")

def get_prop(f: Union["Field", "Structure"], prop: str) -> Union[str, bool]:
    from formulaic.core import Field, Structure

    if isinstance(f, Field):
        return getattr(f, prop)
    elif isinstance(f, Structure):
        return getattr(f.ref_, prop)
    else:
        raise TypeError("Expected Field or Structure instance.")

def expand(data:Union[dict, "FormulaicObject", "FormulaicMixin"], struct:"Structure"=None):
    """
    Takes one of the possible options for the `data` object, and returns
    the "highest" order object, and all its lower order objects unpacked.

    This is useful if you have a function which takes one of those, and you
    want to get at, say, the data, and you don't want to have to do all the
    tests this function does yourself.

    You can do:

    mixin, fo, struct, data = unity.expand(data, struct)

    and be sure that at the very least `data` contains the data

    The rest can be checked for NoneType.

    :param data:
    :param struct:
    :return:
    """
    from formulaic.objects import FormulaicObject, FormulaicMixin

    mixin = None
    fo = None
    d = data
    s = struct

    if isinstance(data, FormulaicObject):
        fo = data
        d = data.data
        s = fo.struct

    elif isinstance(data, FormulaicMixin):
        mixin = data
        fo = data.fo
        d = fo.data
        s = fo.struct

    return mixin, fo, s, d

def get_capability(f: Union["Field", "Structure", "StructRef"], capability: tuple[type, type]) -> Union["FieldCapability", "StructureCapability"]:
    from formulaic.core import Field, Structure, StructRef

    if isinstance(f, Field):
        return f.get_capability(capability[0])
    elif isinstance(f, Structure):
        return f.ref_.get_capability(capability[1])
    elif isinstance(f, StructRef):
        return f.get_capability(capability[1])
    else:
        raise TypeError("Expected Field or Structure instance.")