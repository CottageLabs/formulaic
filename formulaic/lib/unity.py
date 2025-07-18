from typing import Union

from formulaic.core import Field, Structure


def is_required(f: Union[Field, Structure]) -> bool:
    return (isinstance(f, Field) and f.required) or (isinstance(f, Structure) and f._ref.required)

def path(f: Union[Field, Structure]) -> str:
    if isinstance(f, Field):
        return f.path
    elif isinstance(f, Structure):
        return f._ref.path
    else:
        raise TypeError("Expected Field or Structure instance.")

def name(f: Union[Field, Structure]) -> str:
    if isinstance(f, Field):
        return f.name
    elif isinstance(f, Structure):
        return f._name
    else:
        raise TypeError("Expected Field or Structure instance.")