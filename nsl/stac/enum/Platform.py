from epl.protobuf.stac_pb2 import Eo

__all__ = [
    Eo.Platform.keys()
]

UNKNOWN_PLATFORM = Eo.UNKNOWN_PLATFORM
LANDSAT_1 = Eo.LANDSAT_1
LANDSAT_2 = Eo.LANDSAT_2
LANDSAT_3 = Eo.LANDSAT_3
LANDSAT_123 = Eo.LANDSAT_123
LANDSAT_4 = Eo.LANDSAT_4
LANDSAT_5 = Eo.LANDSAT_5
LANDSAT_45 = Eo.LANDSAT_45
LANDSAT_7 = Eo.LANDSAT_7
LANDSAT_8 = Eo.LANDSAT_8
SWIFT_2 = Eo.SWIFT_2


def Value(name):
    return Eo.Platform.Value(name)


def keys():
    return Eo.Platform.keys()


def Name(number):
    return Eo.Platform.Name(number=number)
