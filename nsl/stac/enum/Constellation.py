from epl.protobuf.stac_pb2 import Eo

__all__ = [
    Eo.Constellation.keys()
]

UNKNOWN_PLATFORM = Eo.UNKNOWN_CONSTELLATION
LANDSAT = Eo.LANDSAT
NAIP = Eo.NAIP
SWIFT = Eo.SWIFT
PNOA = Eo.PNOA


def Value(name):
    return Eo.Constellaion.Value(name)


def keys():
    return Eo.Constellaion.keys()


def Name(number):
    return Eo.Constellaion.Name(number=number)

