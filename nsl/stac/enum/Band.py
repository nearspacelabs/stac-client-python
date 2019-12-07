from epl.protobuf.stac_pb2 import Eo

__all__ = Eo.Band.keys()

UNKNOWN_BAND = Eo.UNKNOWN_BAND
COASTAL = Eo.COASTAL
BLUE = Eo.BLUE
GREEN = Eo.GREEN
RED = Eo.RED
RGB = Eo.RGB
NIR = Eo.NIR
# special case for landsat 1 - 3
NIR_2 = Eo.NIR_2
RGBIR = Eo.RGBIR
SWIR_1 = Eo.SWIR_1
SWIR_2 = Eo.SWIR_2
PAN = Eo.PAN
CIRRUS = Eo.CIRRUS
LWIR_1 = Eo.LWIR_1
LWIR_2 = Eo.LWIR_2


def Value(name):
    return Eo.Band.Value(name)


def keys():
    return Eo.Band.keys()


def Name(number):
    return Eo.Band.Name(number=number)


for key, num in Eo.Band.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
