from epl.protobuf.query_pb2 import SortDirection as _SortDirection

__all__ = _SortDirection.keys()


NOT_SORTED = _SortDirection.NOT_SORTED
DESC = _SortDirection.DESC
ASC = _SortDirection.ASC


def Value(name):
    return _SortDirection.Value(name)


def keys():
    return _SortDirection.keys()


def Name(number):
    return _SortDirection.Name(number=number)


for key, num in _SortDirection.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
