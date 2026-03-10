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