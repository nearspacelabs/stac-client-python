from epl.protobuf.stac_pb2 import Eo as _Eo

__all__ = _Eo.Constellation.keys()

UNKNOWN_PLATFORM = _Eo.UNKNOWN_CONSTELLATION
LANDSAT = _Eo.LANDSAT
NAIP = _Eo.NAIP
SWIFT = _Eo.SWIFT
PNOA = _Eo.PNOA


def Value(name):
    return _Eo.Constellaion.Value(name)


def keys():
    return _Eo.Constellaion.keys()


def Name(number):
    return _Eo.Constellaion.Name(number=number)


for key, num in _Eo.Constellation.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
