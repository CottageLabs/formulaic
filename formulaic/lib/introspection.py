def attributes(obj, include_private=False):
    for attr in dir(obj):
        if attr.startswith("_") and not include_private:
            continue
        value = getattr(obj, attr)
        yield attr, value