from ast import literal_eval
from .exceptions import CannotDeduceType

_COMPOUND_TYPES = [list, tuple, dict]
_VALUES_FOR_TRUE = ['yes', 'y', 'true', 't']
_VALUES_FOR_FALSE = ['no', 'n', 'false', 'f']

def coerce_leaf_value(path, value, leaf):
    if leaf is None:
        raise CannotDeduceType("Cannot deduce type of path {0!r}".format(path))
    leaf_type = type(leaf)
    if leaf_type is bool:
        value = value.lower()
        if value not in _VALUES_FOR_TRUE and value not in _VALUES_FOR_FALSE:
            raise ValueError('Invalid value for boolean: {0!r}'.format(value))
        return value in _VALUES_FOR_TRUE
    if leaf_type in _COMPOUND_TYPES:
        return literal_eval(value)
    return leaf_type(value)

def get_config_object_from_proxy(proxy):
    return proxy._conf
