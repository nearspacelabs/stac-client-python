from epl.protobuf.stac_pb2 import *


__all__ = [
    AssetType.keys()
]


def Value(name):
    return AssetType.Value(name)


def keys():
    return AssetType.keys()


def Name(number):
    return AssetType.Name(number=number)
