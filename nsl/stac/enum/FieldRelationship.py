from epl.protobuf.query_pb2 import FieldRelationship

__all__ = FieldRelationship.keys()

EQ = FieldRelationship.EQ
LT_OR_EQ = FieldRelationship.LT_OR_EQ
GT_OR_EQ = FieldRelationship.GT_OR_EQ
LT = FieldRelationship.LT
GT = FieldRelationship.GT
BETWEEN = FieldRelationship.BETWEEN
NOT_BETWEEN = FieldRelationship.NOT_BETWEEN
NOT_EQ = FieldRelationship.NOT_EQ
IN = FieldRelationship.IN
NOT_IN = FieldRelationship.NOT_IN
LIKE = FieldRelationship.LIKE
NOT_LIKE = FieldRelationship.NOT_LIKE


def Value(name):
    return FieldRelationship.Value(name)


def keys():
    return FieldRelationship.keys()


def Name(number):
    return FieldRelationship.Name(number=number)


for key, num in FieldRelationship.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
