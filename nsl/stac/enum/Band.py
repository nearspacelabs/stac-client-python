from epl.protobuf.stac_pb2 import Eo as _Eo

__all__ = _Eo.Band.keys()

UNKNOWN_BAND = _Eo.UNKNOWN_BAND
COASTAL = _Eo.COASTAL
BLUE = _Eo.BLUE
GREEN = _Eo.GREEN
RED = _Eo.RED
RGB = _Eo.RGB
NIR = _Eo.NIR
# special case for landsat 1 - 3
NIR_2 = _Eo.NIR_2
RGBIR = _Eo.RGBIR
SWIR_1 = _Eo.SWIR_1
SWIR_2 = _Eo.SWIR_2
PAN = _Eo.PAN
CIRRUS = _Eo.CIRRUS
LWIR_1 = _Eo.LWIR_1
LWIR_2 = _Eo.LWIR_2


def Value(name):
    return _Eo.Band.Value(name)


def keys():
    return _Eo.Band.keys()


def Name(number):
    return _Eo.Band.Name(number=number)


for key, num in _Eo.Band.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
