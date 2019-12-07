from epl.protobuf.stac_pb2 import Eo as _Eo

__all__ = _Eo.Platform.keys()

UNKNOWN_PLATFORM = _Eo.UNKNOWN_PLATFORM
LANDSAT_1 = _Eo.LANDSAT_1
LANDSAT_2 = _Eo.LANDSAT_2
LANDSAT_3 = _Eo.LANDSAT_3
LANDSAT_123 = _Eo.LANDSAT_123
LANDSAT_4 = _Eo.LANDSAT_4
LANDSAT_5 = _Eo.LANDSAT_5
LANDSAT_45 = _Eo.LANDSAT_45
LANDSAT_7 = _Eo.LANDSAT_7
LANDSAT_8 = _Eo.LANDSAT_8
SWIFT_2 = _Eo.SWIFT_2


def Value(name):
    return _Eo.Platform.Value(name)


def keys():
    return _Eo.Platform.keys()


def Name(number):
    return _Eo.Platform.Name(number=number)


for key, num in _Eo.Platform.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
