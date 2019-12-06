from epl.protobuf.query_pb2 import *

__all__ = [
    SortDirection.keys()
]


def Value(name):
    return SortDirection.Value(name)


def keys():
    return SortDirection.keys()


def Name(number):
    return SortDirection.Name(number=number)
