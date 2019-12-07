# ugly, but intellisense
from epl.protobuf.stac_pb2 import AssetType

__all__ = AssetType.keys()

UNKNOWN_ASSET = AssetType.UNKNOWN_ASSET
JPEG = AssetType.JPEG
GEOTIFF = AssetType.GEOTIFF
LERC = AssetType.LERC
MRF = AssetType.MRF
MRF_IDX = AssetType.MRF_IDX
MRF_XML = AssetType.MRF_XML
CO_GEOTIFF = AssetType.CO_GEOTIFF
RAW = AssetType.RAW
THUMBNAIL = AssetType.THUMBNAIL
TIFF = AssetType.TIFF
JPEG_2000 = AssetType.JPEG_2000
XML = AssetType.XML
TXT = AssetType.TXT
PNG = AssetType.PNG
OVERVIEW = AssetType.OVERVIEW
JSON = AssetType.JSON
HTML = AssetType.HTML
# WEBP = AssetType.WEBP


def Value(name):
    return AssetType.Value(name)


def keys():
    return AssetType.keys()


def Name(number):
    return AssetType.Name(number=number)


for key, num in AssetType.items():
    if key not in __all__:
        raise Exception("protobuf key {} not accounted for in enum".format(key))
