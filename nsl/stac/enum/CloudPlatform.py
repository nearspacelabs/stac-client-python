from epl.protobuf.stac_pb2 import CloudPlatform

__all__ = CloudPlatform.keys()

UNKNOWN_CLOUD_PLATFORM = CloudPlatform.UNKNOWN_CLOUD_PLATFORM
AWS = CloudPlatform.AWS
GCP = CloudPlatform.GCP
AZURE = CloudPlatform.AZURE


def Value(name):
    return CloudPlatform.Value(name)


def keys():
    return CloudPlatform.keys()


def Name(number):
    return CloudPlatform.Name(number=number)


for key, num in CloudPlatform.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
