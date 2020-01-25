# Copyright 2019-20 Near Space Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# for additional information, contact:
#   info@nearspacelabs.com

import sys
from epl.protobuf.stac_pb2 import AssetType as _AssetType
from epl.protobuf.stac_pb2 import CloudPlatform as _CloudPlatform
from epl.protobuf.query_pb2 import FieldRelationship as _FieldRelationship
from epl.protobuf.query_pb2 import SortDirection as _SortDirection
from epl.protobuf.stac_pb2 import Eo as _Eo
from enum import IntFlag

__all__ = ['AssetType', 'CloudPlatform', 'FieldRelationship', 'SortDirection', 'Platform', 'Constellation', 'Band',
           'Instrument']


class AssetType(IntFlag):
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
    WEBP = _AssetType.WEBP


class Band(IntFlag):
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


class SortDirection(IntFlag):
    NOT_SORTED = _SortDirection.NOT_SORTED
    DESC = _SortDirection.DESC
    ASC = _SortDirection.ASC


class CloudPlatform(IntFlag):
    UNKNOWN_CLOUD_PLATFORM = _CloudPlatform.UNKNOWN_CLOUD_PLATFORM
    AWS = _CloudPlatform.AWS
    GCP = _CloudPlatform.GCP
    AZURE = _CloudPlatform.AZURE


class Constellation(IntFlag):
    UNKNOWN_PLATFORM = _Eo.UNKNOWN_CONSTELLATION
    LANDSAT = _Eo.LANDSAT
    NAIP = _Eo.NAIP
    SWIFT = _Eo.SWIFT
    PNOA = _Eo.PNOA


class FieldRelationship(IntFlag):
    EQ = _FieldRelationship.EQ
    LT_OR_EQ = _FieldRelationship.LT_OR_EQ
    GT_OR_EQ = _FieldRelationship.GT_OR_EQ
    LT = _FieldRelationship.LT
    GT = _FieldRelationship.GT
    BETWEEN = _FieldRelationship.BETWEEN
    NOT_BETWEEN = _FieldRelationship.NOT_BETWEEN
    NOT_EQ = _FieldRelationship.NOT_EQ
    IN = _FieldRelationship.IN
    NOT_IN = _FieldRelationship.NOT_IN
    LIKE = _FieldRelationship.LIKE
    NOT_LIKE = _FieldRelationship.NOT_LIKE


class Instrument(IntFlag):
    UNKNOWN_INSTRUMENT = _Eo.UNKNOWN_INSTRUMENT
    OLI = _Eo.OLI
    TIRS = _Eo.TIRS
    OLI_TIRS = _Eo.OLI_TIRS
    POM_1 = _Eo.POM_1
    TM = _Eo.TM
    ETM = _Eo.ETM
    MSS = _Eo.MSS


class Platform(IntFlag):
    UNKNOWN_PLATFORM = _Eo.UNKNOWN_PLATFORM
    LANDSAT_1 = _Eo.LANDSAT_1
    LANDSAT_2 = _Eo.LANDSAT_2
    LANDSAT_3 = _Eo.LANDSAT_3
    LANDSAT_123 = _Eo.LANDSAT_123
    LANDSAT_4 = _Eo.LANDSAT_4
    LANDSAT_5 = _Eo.LANDSAT_5
    LANDSAT_45 = _Eo.LANDSAT_45
    LANDSAT_7 = _Eo.LANDSAT_7
    LANDSAT_8 = _Eo.LANDSAT_8
    SWIFT_2 = _Eo.SWIFT_2


# Final check to make sure that all enums have complete definitions for the associated protobufs
for enum_class_name in __all__:
    nsl_enum = getattr(sys.modules[__name__], enum_class_name)
    if enum_class_name in ['Platform', 'Constellation', 'Band', 'Instrument']:
        eo_class = getattr(sys.modules[__name__], '_Eo')
        epl_pb_enum_wrapper = getattr(eo_class, enum_class_name)
    else:
        epl_pb_enum_wrapper = getattr(sys.modules[__name__], '_' + enum_class_name)

    for enum_key_name, num in epl_pb_enum_wrapper.items():
        enum_values = [member[1].value for member in nsl_enum.__members__.items()]
        if num not in enum_values:
            raise Exception("protobuf enum_class_name {} not accounted for in enum {}. the stac client hasn't been "
                            "updated for this version of the protobuf definition".format(enum_key_name,
                                                                                         enum_class_name))
