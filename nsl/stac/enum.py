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
from epl.protobuf.v1.stac_pb2 import AssetType as _AssetType
from epl.protobuf.v1.stac_pb2 import CloudPlatform as _CloudPlatform
from epl.protobuf.v1.query_pb2 import FilterRelationship as _FilterRelationship
from epl.protobuf.v1.query_pb2 import SortDirection as _SortDirection
from epl.protobuf.v1.stac_pb2 import Constellation as _Constellation
from epl.protobuf.v1.stac_pb2 import Mission as _Mission
from epl.protobuf.v1.stac_pb2 import Instrument as _Instrument
from epl.protobuf.v1.stac_pb2 import Platform as _Platform
from epl.protobuf.v1.stac_pb2 import Eo as _Eo

from enum import IntFlag

__all__ = ['AssetType', 'CloudPlatform', 'FilterRelationship', 'SortDirection', 'Platform', 'Constellation', 'Band',
           'Instrument', 'Mission']


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
    IBM = _CloudPlatform.IBM


class Constellation(IntFlag):
    UNKNOWN_PLATFORM = _Constellation.UNKNOWN_CONSTELLATION


class Mission(IntFlag):
    UNKNOWN_MISSION = _Mission.UNKNOWN_MISSION
    LANDSAT = _Mission.LANDSAT
    NAIP = _Mission.NAIP
    SWIFT = _Mission.SWIFT
    PNOA = _Mission.PNOA


class FilterRelationship(IntFlag):
    EQ = _FilterRelationship.EQ
    LTE = _FilterRelationship.LTE
    GTE = _FilterRelationship.GTE
    LT = _FilterRelationship.LT
    GT = _FilterRelationship.GT
    BETWEEN = _FilterRelationship.BETWEEN
    NOT_BETWEEN = _FilterRelationship.NOT_BETWEEN
    NEQ = _FilterRelationship.NEQ
    IN = _FilterRelationship.IN
    NOT_IN = _FilterRelationship.NOT_IN
    LIKE = _FilterRelationship.LIKE
    NOT_LIKE = _FilterRelationship.NOT_LIKE


class Instrument(IntFlag):
    UNKNOWN_INSTRUMENT = _Instrument.UNKNOWN_INSTRUMENT
    OLI = _Instrument.OLI
    TIRS = _Instrument.TIRS
    OLI_TIRS = _Instrument.OLI_TIRS
    POM_1 = _Instrument.POM_1
    TM = _Instrument.TM
    ETM = _Instrument.ETM
    MSS = _Instrument.MSS
    POM_2 = _Instrument.POM_2


class Platform(IntFlag):
    UNKNOWN_PLATFORM = _Platform.UNKNOWN_PLATFORM
    LANDSAT_1 = _Platform.LANDSAT_1
    LANDSAT_2 = _Platform.LANDSAT_2
    LANDSAT_3 = _Platform.LANDSAT_3
    LANDSAT_123 = _Platform.LANDSAT_123
    LANDSAT_4 = _Platform.LANDSAT_4
    LANDSAT_5 = _Platform.LANDSAT_5
    LANDSAT_45 = _Platform.LANDSAT_45
    LANDSAT_7 = _Platform.LANDSAT_7
    LANDSAT_8 = _Platform.LANDSAT_8
    SWIFT_2 = _Platform.SWIFT_2
    SWIFT_3 = _Platform.SWIFT_3


# Final check to make sure that all enums have complete definitions for the associated protobufs
for enum_class_name in __all__:
    nsl_enum = getattr(sys.modules[__name__], enum_class_name)
    if enum_class_name in ['Band']:
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
