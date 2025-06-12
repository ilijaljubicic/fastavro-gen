from dataclasses import fields, is_dataclass
from typing import get_origin, get_args, Literal, ForwardRef, Union
from fastavro_gen.logical_types import LOGICAL_TYPE_MAP

PRIMITIVES = {str, int, float, bool}


def fields_dict(cls):
    """Turn tuple of fields to dict"""
    return {f.name: f.type for f in fields(cls)}


def fromdict(cls, record):
    """Transform a dictionary to dataclass cls"""
    _fields = fields_dict(cls)
    return cls(**{k: _handle_type(_fields[k], v, cls=cls) for k, v in record.items()})



def _handle_type(_type, val, cls):
    """Helper method to handle different types"""
    # 0) Nulls
    if val is None:
        return None

    # 1) If it's already the right Python type, just return it
    try:
        if isinstance(val, _type):
            return val
    except Exception:
        # some typing constructs don't work with isinstance
        pass

    # 2) Empty containers / falsey values
    if not val:
        return val
    if _type in PRIMITIVES:
        return val

    # 3) LogicalType‐based parsing
    lt = getattr(_type, "logicalType", None)
    if lt in LOGICAL_TYPE_MAP:
        _, _, parser = LOGICAL_TYPE_MAP[lt]
        return parser(val)

    # 4) Dataclasses → recurse
    if is_dataclass(_type):
        return fromdict(_type, val)

    # 5) Generics via get_origin / get_args
    origin = get_origin(_type)
    args = get_args(_type)

    #   a) Literal[...] → raw value
    if origin is Literal:
        return val

    #   b) List[T]
    if origin is list:
        (subtype,) = args
        return [_handle_type(subtype, v, cls) for v in val]

    #   c) Dict[K, V]
    if origin is dict:
        key_t, val_t = args
        # forward‐ref to same dataclass?
        if any(isinstance(a, ForwardRef) for a in args):
            return cls(**{
                k: _handle_type(cls.__annotations__[k], v, cls)
                for k, v in val.items()
            })
        # plain dict[K, V]
        return {
            k: _handle_type(val_t, v, cls)
            for k, v in val.items()
        }

    #   d) Union[...] (incl. Optional)
    if origin is Union:
        for subtype in args:
            try:
                return _handle_type(subtype, val, cls)
            except Exception:
                pass

    # 6) Give up
    raise Exception(f"Failed parsing value {val!r} with type {_type}")
