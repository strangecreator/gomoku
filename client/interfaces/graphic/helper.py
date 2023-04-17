from types import SimpleNamespace


def to_dict(obj: SimpleNamespace) -> dict:
    result = {}
    for name, value in vars(obj).items():
        result[name] = value if not isinstance(value, SimpleNamespace) else to_dict(value)
    return result