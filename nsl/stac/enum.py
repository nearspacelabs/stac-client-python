from epl.protobuf.stac_pb2 import AssetType, TXT, THUMBNAIL, CO_GEOTIFF, GEOTIFF, MRF
from epl.protobuf.stac_pb2 import AWS, GCP, UNKNOWN_CLOUD_PLATFORM, CloudPlatform
from epl.protobuf.query_pb2 import SortDirection, NOT_SORTED, ASC, DESC
from epl.protobuf.query_pb2 import FieldRelationship, EQ, LT, GT, LT_OR_EQ, GT_OR_EQ, BETWEEN, NOT_BETWEEN, IN, NOT_IN, \
    NOT_EQ
from epl.protobuf.stac_pb2 import Eo


BLUE = Eo.BLUE
RED = Eo.RED
GREEN = Eo.GREEN
RGB = Eo.RGB
RGBIR = Eo.RGBIR
LWIR_1 = Eo.LWIR_1
CIRRUS = Eo.CIRRUS
LANDSAT = Eo.LANDSAT

__all__ = [
    'RGB', 'RGBIR', 'RED', 'GREEN', 'BLUE',
    'AssetType', 'CO_GEOTIFF', 'GEOTIFF', 'MRF', 'TXT', 'THUMBNAIL',
    'CloudPlatform', 'AWS', 'GCP', 'UNKNOWN_CLOUD_PLATFORM',
    'FieldRelationship', 'EQ', 'LT', 'GT', 'LT_OR_EQ', 'GT_OR_EQ', 'BETWEEN', 'NOT_BETWEEN', 'IN', 'NOT_IN', 'NOT_EQ',
    'SortDirection', 'NOT_SORTED', 'ASC', 'DESC',

]
