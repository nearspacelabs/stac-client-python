from epl.protobuf.query_pb2 import *

__all__ = [
    FieldRelationship.keys()
]


def Value(name):
    return FieldRelationship.Value(name)


def keys():
    return FieldRelationship.keys()


def Name(number):
    return FieldRelationship.Name(number=number)
