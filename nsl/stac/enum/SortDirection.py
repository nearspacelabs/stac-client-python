from epl.protobuf.query_pb2 import SortDirection

__all__ = SortDirection.keys()


NOT_SORTED = SortDirection.NOT_SORTED
DESC = SortDirection.DESC
ASC = SortDirection.ASC


def Value(name):
    return SortDirection.Value(name)


def keys():
    return SortDirection.keys()


def Name(number):
    return SortDirection.Name(number=number)


for key, num in SortDirection.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
