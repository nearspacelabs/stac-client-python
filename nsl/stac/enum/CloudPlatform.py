from epl.protobuf.stac_pb2 import CloudPlatform as _CloudPlatform

__all__ = _CloudPlatform.keys()

UNKNOWN_CLOUD_PLATFORM = _CloudPlatform.UNKNOWN_CLOUD_PLATFORM
AWS = _CloudPlatform.AWS
GCP = _CloudPlatform.GCP
AZURE = _CloudPlatform.AZURE


def Value(name):
    return _CloudPlatform.Value(name)


def keys():
    return _CloudPlatform.keys()


def Name(number):
    return _CloudPlatform.Name(number=number)


for key, num in _CloudPlatform.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
