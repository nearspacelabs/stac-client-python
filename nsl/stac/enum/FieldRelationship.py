from epl.protobuf.query_pb2 import FieldRelationship as _FieldRelationship

__all__ = _FieldRelationship.keys()

EQ = _FieldRelationship.EQ
LT_OR_EQ = _FieldRelationship.LT_OR_EQ
GT_OR_EQ = _FieldRelationship.GT_OR_EQ
LT = _FieldRelationship.LT
GT = _FieldRelationship.GT
BETWEEN = _FieldRelationship.BETWEEN
NOT_BETWEEN = _FieldRelationship.NOT_BETWEEN
NOT_EQ = _FieldRelationship.NOT_EQ
IN = _FieldRelationship.IN
NOT_IN = _FieldRelationship.NOT_IN
LIKE = _FieldRelationship.LIKE
NOT_LIKE = _FieldRelationship.NOT_LIKE


def Value(name):
    return _FieldRelationship.Value(name)


def keys():
    return _FieldRelationship.keys()


def Name(number):
    return _FieldRelationship.Name(number=number)


for key, num in _FieldRelationship.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
