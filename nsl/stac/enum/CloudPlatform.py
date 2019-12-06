from epl.protobuf.stac_pb2 import *

__all__ = [
    CloudPlatform.keys()
]


def Value(name):
    return CloudPlatform.Value(name)


def keys():
    return CloudPlatform.keys()


def Name(number):
    return CloudPlatform.Name(number=number)
