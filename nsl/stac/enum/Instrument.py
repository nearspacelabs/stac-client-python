from epl.protobuf.stac_pb2 import Eo

__all__ = [
    Eo.Instrument.keys()
]

UNKNOWN_INSTRUMENT = Eo.UNKNOWN_INSTRUMENT
OLI = Eo.OLI
TIRS = Eo.TIRS
OLI_TIRS = Eo.OLI_TIRS
POM_1 = Eo.POM_1
TM = Eo.TM
ETM = Eo.ETM
MSS = Eo.MSS


def Value(name):
    return Eo.Instrument.Value(name)


def keys():
    return Eo.Instrument.keys()


def Name(number):
    return Eo.Instrument.Name(number=number)
