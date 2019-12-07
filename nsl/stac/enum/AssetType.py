# ugly, but intellisense
from epl.protobuf.stac_pb2 import AssetType as _AssetType

__all__ = _AssetType.keys()

UNKNOWN_ASSET = _AssetType.UNKNOWN_ASSET
JPEG = _AssetType.JPEG
GEOTIFF = _AssetType.GEOTIFF
LERC = _AssetType.LERC
MRF = _AssetType.MRF
MRF_IDX = _AssetType.MRF_IDX
MRF_XML = _AssetType.MRF_XML
CO_GEOTIFF = _AssetType.CO_GEOTIFF
RAW = _AssetType.RAW
THUMBNAIL = _AssetType.THUMBNAIL
TIFF = _AssetType.TIFF
JPEG_2000 = _AssetType.JPEG_2000
XML = _AssetType.XML
TXT = _AssetType.TXT
PNG = _AssetType.PNG
OVERVIEW = _AssetType.OVERVIEW
JSON = _AssetType.JSON
HTML = _AssetType.HTML
# WEBP = _AssetType.WEBP


def Value(name):
    return _AssetType.Value(name)


def keys():
    return _AssetType.keys()


def Name(number):
    return _AssetType.Name(number=number)


for key, num in _AssetType.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
