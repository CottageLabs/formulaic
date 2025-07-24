from __future__ import annotations
from typing import Union


def is_required(f: Union["Field", "Structure"]) -> bool:
    from formulaic.core import Field, Structure

    return (isinstance(f, Field) and f.required) or (isinstance(f, Structure) and f._ref.required)


def path(f: Union["Field", "Structure"]) -> str:
    from formulaic.core import Field, Structure

    if isinstance(f, Field):
        return f.path
    elif isinstance(f, Structure):
        return f._ref.path
    else:
        raise TypeError("Expected Field or Structure instance.")


def name(f: Union["Field", "Structure"]) -> str:
    from formulaic.core import Field, Structure

    if isinstance(f, Field):
        return f.name
    elif isinstance(f, Structure):
        return f._name
    else:
        raise TypeError("Expected Field or Structure instance.")


def clone(f: Union["Field", "Structure"]) -> Union["Field", "Structure"]:
    from formulaic.core import Field, Structure

    if isinstance(f, Field):
        return f.__class__(need=f.need, multiplicity=f.multiplicity,
                              duplicability=f.duplicability, parent=f.parent)
    elif isinstance(f, Structure):
        return f.__class__(f._ref.need, f._ref.multiplicity, f._ref.parent)
    else:
        raise TypeError("Expected Field or Structure instance.")