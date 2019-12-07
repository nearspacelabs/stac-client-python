from epl.protobuf.stac_pb2 import Eo as _Eo

__all__ = _Eo.Instrument.keys()

UNKNOWN_INSTRUMENT = _Eo.UNKNOWN_INSTRUMENT
OLI = _Eo.OLI
TIRS = _Eo.TIRS
OLI_TIRS = _Eo.OLI_TIRS
POM_1 = _Eo.POM_1
TM = _Eo.TM
ETM = _Eo.ETM
MSS = _Eo.MSS


def Value(name):
    return _Eo.Instrument.Value(name)


def keys():
    return _Eo.Instrument.keys()


def Name(number):
    return _Eo.Instrument.Name(number=number)


for key, num in _Eo.Instrument.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
