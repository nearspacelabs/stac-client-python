import re

import boto3
import botocore.exceptions

from datetime import date, timezone
from datetime import datetime as internal_datetime
from typing import Union, Iterator, List, Tuple

from epl.protobuf.v1.geometry_pb2 import ProjectionData
from google.protobuf.any_pb2 import Any
from google.protobuf.wrappers_pb2 import FloatValue
from epl.geometry import BaseGeometry, Polygon

from nsl.stac import StacItem, StacRequest, View, ViewRequest, \
    Mosaic, MosaicRequest, Eo, EoRequest, EnvelopeData, FloatFilter, Asset, enum, utils
from nsl.stac.client import NSLClient
from nsl.stac import stac_service as stac_singleton


def _set_properties(stac_data, properties, type_url_prefix):
    """
     pack properties and then set the properties member value to the input.
     :param stac_data:
     :param properties:
     :param type_url_prefix:
     :return:
     """
    if properties is None:
        return

    # pack the properties into an Any field
    packed_properties = Any()
    packed_properties.Pack(properties,
                           type_url_prefix=type_url_prefix + properties.DESCRIPTOR.full_name)

    # overwrite the previous properties field with this updated version
    stac_data.properties.CopyFrom(packed_properties)
    properties = properties
    return stac_data, properties


def _check_assets_exist(stac_item: StacItem, b_raise=True):
    results = []
    for asset_key in stac_item.assets:
        asset = stac_item.assets[asset_key]
        b_file_exists = _check_asset_exists(asset)

        if not b_file_exists and b_raise:
            raise ValueError("get_blob_metadata returns false for asset key {}".format(asset_key))
        results.append(asset_key)
    return results


def _check_asset_exists(asset: Asset) -> bool:
    if asset.cloud_platform == enum.CloudPlatform.GCP:
        return utils.get_blob_metadata(bucket=asset.bucket, blob_name=asset.object_path) is not None
    elif asset.cloud_platform == enum.CloudPlatform.AWS:
        return _check_aws_asset_exists(asset)
    else:
        raise ValueError("cloud platform {0} of asset {1} not supported"
                         .format(enum.CloudPlatform(asset.cloud_platform).name, asset))


def _check_aws_asset_exists(asset: Asset) -> bool:
    s3 = boto3.client('s3')

    try:
        s3.head_object(Bucket=asset.bucket, Key=asset.object_path, RequestPayer='requester')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise e
    return True


class AssetWrap:
    def __init__(self,
                 asset: Asset = None,
                 bucket: str = None,
                 object_path: str = None,
                 asset_type: enum.AssetType = enum.AssetType.UNKNOWN_ASSET,
                 eo_bands: enum.Band = enum.Band.UNKNOWN_BAND,
                 href="",
                 cloud_platform: enum.CloudPlatform = enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
                 bucket_manager: str = "",
                 bucket_region: str = ""):
        if asset is None:
            href_type = self.asset_type_details(asset_type=asset_type,
                                                b_thumbnail_png=asset_type == enum.AssetType.THUMBNAIL)
            self._asset = Asset(href=href,
                                type=href_type,
                                eo_bands=eo_bands,
                                asset_type=asset_type,
                                cloud_platform=cloud_platform,
                                bucket_manager=bucket_manager,
                                bucket_region=bucket_region,
                                bucket=bucket,
                                object_path=object_path)
        else:
            href_type = self.asset_type_details(asset_type=asset.asset_type,
                                                b_thumbnail_png=asset.asset_type == enum.AssetType.THUMBNAIL)

        self._ext = href_type[0]
        self._type = href_type[1]
        self._asset = asset

    def __str__(self):
        return str("{0}extension: {1}".format(self._asset, self._ext))

    @property
    def asset_type(self) -> enum.AssetType:
        """
type of asset
        :return:
        """
        return self._asset.asset_type

    @property
    def bucket(self) -> str:
        """
bucket where data stored. may be private
        :return:
        """
        return self._asset.bucket

    @property
    def bucket_manager(self) -> str:
        return self._asset.bucket_manager

    @property
    def bucket_region(self) -> str:
        return self._asset.bucket_region

    @property
    def cloud_platform(self) -> enum.CloudPlatform:
        """
cloud platform where data stored. Google Cloud, AWS and Azure are current options (or unknown)
        :return:
        """
        return self._asset.cloud_platform

    @property
    def eo_bands(self) -> enum.Band:
        """
electro optical bands included in data. if data is not electro optical, then this is set to Unknown
        :return:
        """
        return self._asset.eo_bands

    @property
    def ext(self) -> str:
        return self._ext

    @property
    def href(self) -> str:
        """
the href for downloading data
        :return:
        """
        return self._asset.href

    @property
    def object_path(self) -> str:
        """
the object path to use with the bucket if access is available
        :return:
        """
        return self._asset.object_path

    @property
    def type(self) -> str:
        return self._type

    def equals(self, other: Asset):
        """
does the AssetWrap equal a protobuf Asset
        :param other:
        :return:
        """
        return self._asset.href == other.href and \
            self._asset.type == other.type and \
            self._asset.eo_bands == other.eo_bands and \
            self._asset.asset_type == other.asset_type and \
            self._asset.cloud_platform == other.cloud_platform and \
            self._asset.bucket_manager == other.bucket_manager and \
            self._asset.bucket_region == other.bucket_region and \
            self._asset.bucket == other.bucket and \
            self._asset.object_path == other.object_path

    def exists(self) -> bool:
        return _check_asset_exists(self._asset)

    def __eq__(self, other):
        if not isinstance(other, AssetWrap):
            return False

        return self.equals(other._asset)

    @staticmethod
    def asset_type_details(asset_type: enum.AssetType, b_thumbnail_png: bool = True) -> (str, str):
        """
for asset type and bool, get the extension and href type
        :param asset_type:
        :param b_thumbnail_png:
        :return: str extension, str href type
        """
        # TODO finish asset_type map
        ext = "tif"
        if asset_type == enum.AssetType.TIFF:
            href_type = "image/tiff"
        elif asset_type == enum.AssetType.GEOTIFF:
            href_type = "image/vnd.stac.geotiff"
        elif asset_type == enum.AssetType.CO_GEOTIFF:
            href_type = "image/vnd.stac.geotiff; cloud-optimized=true"
        elif (asset_type == enum.AssetType.THUMBNAIL and b_thumbnail_png) or asset_type == enum.AssetType.PNG:
            href_type = "image/png"
            ext = "png"
        elif (asset_type == enum.AssetType.THUMBNAIL and not b_thumbnail_png) or asset_type == enum.AssetType.JPEG:
            href_type = "image/jpeg"
            ext = "jpg"
        elif asset_type == enum.AssetType.JPEG_2000:
            href_type = "image/jp2"
            ext = "jp2"
        elif asset_type == enum.AssetType.MRF_XML:
            href_type = "application/xml"
            ext = "xml"
        else:
            href_type = "application/octet-stream"
            ext = "bin"

        return ext, href_type


class _BaseWrap:
    def __init__(self, stac_data, properties_func, type_url_prefix="nearspacelabs.com/proto/"):
        """
        Whether it's a stac_request or a stac_item, allow for the repack_properties method to work
        :param stac_data:
        :param properties_func:
        """
        self._stac_data = stac_data
        self.properties = None
        self._properties_func = properties_func
        self._type_url_prefix = type_url_prefix

        if stac_data is not None and stac_data.HasField("properties") and properties_func is not None:
            self.properties = properties_func()
            self._stac_data.properties.Unpack(self.properties)
        elif properties_func is not None:
            self.properties = properties_func()
            self._set_properties(self.properties)

    def __str__(self):
        return str(self._stac_data)

    def _set_properties(self, properties):
        self._stac_data, self.properties = _set_properties(self._stac_data, properties, self._type_url_prefix)

    def _get_field(self, metadata_key: str, key: str):
        if self.properties.HasField(metadata_key):
            return getattr(getattr(self.properties, metadata_key), key)
        return None

    def _get_wrapped_field(self, metadata_key: str, key: str):
        if self.properties.HasField(metadata_key):
            return getattr(getattr(getattr(self.properties, metadata_key), key), "value")
        return None

    def _set_internal_sub_object(self, metadata_key: str):
        pass

    def _set_field(self, metadata_key: str, key: str, value):
        self._set_internal_sub_object(metadata_key)
        setattr(getattr(self.properties, metadata_key), key, value)

    def _set_obj(self, metadata_key: str, key: str, value):
        self._set_internal_sub_object(metadata_key)
        getattr(getattr(self.properties, metadata_key), key).CopyFrom(value)

    def _set_nested_obj(self, metadata_key: str, object_key: str, value_key: str, value):
        self._set_internal_sub_object(metadata_key)
        getattr(getattr(getattr(self.properties, metadata_key), object_key), value_key).CopyFrom(value)

    def _set_nested_field(self, metadata_key: str, object_key: str, value_key: str, value):
        setattr(getattr(getattr(self.properties, metadata_key), object_key), value_key, value)

    def _get_nested_field(self, metadata_key: str, object_key: str, value_key: str):
        if self.properties.HasField(metadata_key):
            return getattr(getattr(getattr(self.properties, metadata_key), object_key), value_key)
        return None

    def _get_nested_wrapped_field(self, metadata_key: str, object_key: str, value_key: str):
        if self.properties.HasField(metadata_key):
            return getattr(getattr(getattr(getattr(self.properties, metadata_key), object_key), value_key), "value")
        return None


class StacItemWrap(_BaseWrap):
    """
Wrapper for StacItem protobuf
    """

    def __init__(self, stac_item: StacItem = None, properties_constructor=None):
        self._assets = {}
        if stac_item is None:
            stac_data = StacItem()
        else:
            stac_data = StacItem()
            stac_data.CopyFrom(stac_item)

            for asset_key in stac_data.assets:
                self._assets[asset_key] = AssetWrap(stac_data.assets[asset_key])

        super().__init__(stac_data, properties_constructor)

    @property
    def bounds(self) -> Tuple[float]:
        """
Returns a (minx, miny, maxx, maxy)
        :return: tuple (float values)
        """
        return self.geometry.bounds

    @property
    def bbox(self) -> EnvelopeData:
        """
bounding box of data. In form of EnvelopeData
        :return:
        """
        return self.stac_item.bbox

    @property
    def cloud_cover(self) -> Union[float, None]:
        """
get cloud cover value
        :return: float or None
        """
        if self.stac_item.HasField("eo") and self.stac_item.eo.HasField("cloud_cover"):
            return self.stac_item.eo.cloud_cover.value
        return None

    @cloud_cover.setter
    def cloud_cover(self, value: float):
        if not self.stac_item.HasField("eo"):
            self.stac_item.eo.CopyFrom(Eo(cloud_cover=FloatValue(value=value)))
        else:
            self.stac_item.eo.cloud_cover.CopyFrom(FloatValue(value=value))

    @property
    def collection(self) -> str:
        """
the collection id for the stac item
        :return:
        """
        return self.stac_item.collection

    @collection.setter
    def collection(self, value: str):
        self.stac_item.collection = value

    @property
    def constellation_enum(self):
        """
the enum describing the constellation
        :return:
        """
        return self.stac_item.constellation_enum

    @constellation_enum.setter
    def constellation_enum(self, value: enum.Constellation):
        self.stac_item.constellation_enum = value

    @property
    def created(self) -> Union[internal_datetime, None]:
        if self.stac_item.HasField("created"):
            return internal_datetime.fromtimestamp(self.stac_item.created.seconds, tz=timezone.utc)
        else:
            return None

    @created.setter
    def created(self, value: Union[internal_datetime, date]):
        self.stac_item.created.CopyFrom(utils.pb_timestamp(d_utc=value))

    @property
    def datetime(self):
        return self.observed

    @datetime.setter
    def datetime(self, value: Union[internal_datetime, date]):
        self.observed = value

    @property
    def end_datetime(self):
        return self.stac_item.end_observed

    @end_datetime.setter
    def end_datetime(self, value: Union[internal_datetime, date]):
        self.end_observed = value

    @property
    def end_observed(self):
        return self.stac_item.end_observed

    @end_observed.setter
    def end_observed(self, value: Union[internal_datetime, date]):
        self.stac_item.end_observation.CopyFrom(utils.pb_timestamp(d_utc=value))
        self.stac_item.end_datetime.CopyFrom(utils.pb_timestamp(d_utc=value))

    @property
    def geometry(self) -> BaseGeometry:
        if self.stac_item.HasField("geometry"):
            return BaseGeometry.import_protobuf(self.stac_item.geometry)
        elif self.stac_item.HasField("bbox"):
            return Polygon.from_envelope_data(self.stac_item.bbox)

    @geometry.setter
    def geometry(self, geometry: BaseGeometry):
        self.stac_item.geometry.CopyFrom(geometry.geometry_data)
        self.stac_item.bbox.CopyFrom(geometry.envelope_data)

    @property
    def gsd(self):
        """
        get cloud cover value
        :return: float or None
        """
        if self.stac_item.HasField("gsd"):
            return self.stac_item.gsd.value
        return None

    @gsd.setter
    def gsd(self, value: float):
        self.stac_item.gsd.CopyFrom(FloatValue(value=value))

    @property
    def id(self):
        return self.stac_item.id

    @id.setter
    def id(self, value: str):
        self.stac_item.id = value

    @property
    def instrument_enum(self):
        return self.stac_item.instrument_enum

    @instrument_enum.setter
    def instrument_enum(self, value: enum.Instrument):
        self.stac_item.instrument_enum = value

    @property
    def mission_enum(self):
        return self.stac_item.mission_enum

    @mission_enum.setter
    def mission_enum(self, value: enum.Mission):
        self.stac_item.mission_enum = value

    @property
    def mosaic_name(self):
        if self.stac_item.HasField("mosaic"):
            return self.stac_item.mosaic.name
        return None

    @mosaic_name.setter
    def mosaic_name(self, name: str):
        if not self.stac_item.HasField("mosaic"):
            self.stac_item.mosaic.CopyFrom(Mosaic(name=name))
        else:
            self.stac_item.mosaic.name = name

    @property
    def mosaic_quad_key(self) -> Union[str, None]:
        """
If the STAC item is a quad from a mosaic, then it has a quad key that defines the boundaries of the quad. The quad tree
definition is assumed to be the convention defined by Google Maps, based off of there Pseudo-Web Mercator projection.

An example quad key is '02313012030231'. Quads use 2-bit tile interleaved addresses. The first character defines the
largest quadrant (in this case 0 is upper left), the next character ('2') is the upper right quadrant of that first
quadrant, the 3rd character ('3') is the lower left quadrant of the previous quadrant and so on.

For more details on the quad tree tiling for maps use `openstreetmaps docs
<https://wiki.openstreetmap.org/wiki/QuadTiles#Quadtile_implementation>`
        :return:
        """
        if self.stac_item.HasField("mosaic"):
            return self.stac_item.mosaic.quad_key
        return None

    @mosaic_quad_key.setter
    def mosaic_quad_key(self, quad_key: str):
        if not self.stac_item.HasField("mosaic"):
            self.stac_item.mosaic.CopyFrom(Mosaic(quad_key=quad_key))
        else:
            self.stac_item.mosaic.quad_key = quad_key

    @property
    def observed(self) -> Union[internal_datetime, None]:
        if self.stac_item.HasField("datetime"):
            return internal_datetime.fromtimestamp(self.stac_item.datetime.seconds, tz=timezone.utc)
        elif self.stac_item.HasField("observed"):
            return internal_datetime.fromtimestamp(self.stac_item.observed.seconds, tz=timezone.utc)
        else:
            return None

    @observed.setter
    def observed(self, value: Union[internal_datetime, date]):
        self.stac_item.datetime.CopyFrom(utils.pb_timestamp(d_utc=value))
        self.stac_item.observed.CopyFrom(utils.pb_timestamp(d_utc=value))

    @property
    def off_nadir(self) -> Union[float, None]:
        """
        get cloud cover value
        :return: float or None
        """
        if self.stac_item.HasField("view") and self.stac_item.view.HasField("off_nadir"):
            return self.stac_item.view.off_nadir.value
        return None

    @off_nadir.setter
    def off_nadir(self, value: float):
        if not self.stac_item.HasField("view"):
            self.stac_item.view.CopyFrom(View(off_nadir=FloatValue(value=value)))
        else:
            self.stac_item.view.off_nadir.CopyFrom(FloatValue(value=value))

    @property
    def platform_enum(self):
        return self.stac_item.platform_enum

    @platform_enum.setter
    def platform_enum(self, value: enum.Platform):
        self.stac_item.platform_enum = value

    @property
    def provenance_ids(self):
        """
The stac_ids that went into creating the current mosaic. They are in the array in the order which they were used in
the mosaic
        :return:
        """
        return self.stac_item.mosaic.provenance_ids

    @property
    def proj(self) -> ProjectionData:
        """
The projection for all assets of this STAC item. If an Asset has its own proj definition,
then that supersedes this projection definition.
        :return: projection information
        """
        return self.stac_item.proj

    @proj.setter
    def proj(self, value: ProjectionData):
        self.stac_item.proj.CopyFrom(value)

    @property
    def stac_item(self):
        """
        get stac_item
        :return: StacItem
        """
        return self._stac_data

    @property
    def updated(self) -> Union[internal_datetime, None]:
        if self.stac_item.HasField("updated"):
            return internal_datetime.fromtimestamp(self.stac_item.updated.seconds, tz=timezone.utc)
        else:
            return None

    @updated.setter
    def updated(self, value: Union[internal_datetime, date]):
        self.stac_item.updated.CopyFrom(utils.pb_timestamp(d_utc=value))

    def get_assets(self,
                   asset_key: str = None,
                   asset_type: enum.AssetType = enum.AssetType.UNKNOWN_ASSET,
                   cloud_platform: enum.CloudPlatform = enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
                   eo_bands: enum.Band = enum.Band.UNKNOWN_BAND,
                   asset_key_regex: str = None) -> List[AssetWrap]:
        if asset_key is not None and asset_key in self._assets:
            return [self._assets[asset_key]]

        results = []
        for asset_key in self._assets:
            current = self._assets[asset_key]
            if asset_key_regex is not None and not re.match(asset_key_regex, asset_key):
                continue
            if eo_bands != enum.Band.UNKNOWN_BAND and current.eo_bands != eo_bands:
                continue
            if cloud_platform != enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM and current.cloud_platform != cloud_platform:
                continue
            if asset_type != enum.AssetType.UNKNOWN_ASSET and current.asset_type != asset_type:
                continue

            # check that asset hasn't changed between protobuf and asset_map
            pb_asset = self.stac_item.assets[asset_key]
            if not current.equals(pb_asset):
                raise ValueError("corrupted protobuf. Asset and AssetWrap have differing underlying protobuf")

            results.append(current)
        return results

    def get_asset(self,
                  asset_key: str = None,
                  asset_type: enum.AssetType = enum.AssetType.UNKNOWN_ASSET,
                  cloud_platform: enum.CloudPlatform = enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
                  eo_bands: enum.Band = enum.Band.UNKNOWN_BAND,
                  asset_key_regex: str = None) -> Union[AssetWrap, None]:
        results = self.get_assets(asset_key, asset_type, cloud_platform, eo_bands, asset_key_regex)
        if len(results) > 1:
            raise ValueError("must be more specific in selecting your asset. if all enums are used, try using "
                             "asset_key_regex")
        elif len(results) == 1:
            return results[0]
        return None

    def check_assets_exist(self, b_raise):
        return _check_assets_exist(self.stac_item, b_raise=b_raise)


class StacRequestWrap(_BaseWrap):
    def __init__(self, stac_request: StacRequest = None, properties_constructor=None, id: str = ""):
        if stac_request is None:
            stac_request = StacRequest(id=id)

        super().__init__(stac_request, properties_constructor)

    @property
    def bbox(self) -> EnvelopeData:
        if self.stac_request.HasField("bbox"):
            return self.stac_request.bbox
        elif self.stac_request.HasField("intersects"):
            return self.intersects.envelope_data
        return None

    @bbox.setter
    def bbox(self, value: EnvelopeData):
        # this tests the spatial reference (it would be better to have a dedicated method)
        value = Polygon.from_envelope_data(envelope_data=value).envelope_data
        self.stac_request.bbox.CopyFrom(value)
        self.stac_request.ClearField("intersects")

    @property
    def collection(self) -> str:
        return self.stac_request.collection

    @collection.setter
    def collection(self, value: str):
        self.stac_request.collection = value

    @property
    def constellation_enum(self):
        return self.stac_request.constellation_enum

    @constellation_enum.setter
    def constellation_enum(self, value: enum.Constellation):
        self.stac_request.constellation_enum = value

    @property
    def intersects(self):
        if self.stac_request.HasField("intersects"):
            return BaseGeometry.import_protobuf(self.stac_request.intersects)
        elif self.stac_request.HasField("bbox"):
            return Polygon.from_envelope_data(self.bbox)
        return None

    @intersects.setter
    def intersects(self, geometry: BaseGeometry):
        self.stac_request.intersects.CopyFrom(geometry.geometry_data)
        self.stac_request.ClearField("bbox")

    @property
    def id(self):
        return self.stac_request.id

    @id.setter
    def id(self, value):
        self.stac_request.id = value

    @property
    def instrument_enum(self):
        return self.stac_request.instrument_enum

    @instrument_enum.setter
    def instrument_enum(self, value: enum.Instrument):
        self.stac_request.instrument_enum = value

    @property
    def limit(self):
        return self.stac_request.limit

    @limit.setter
    def limit(self, value: int):
        self.stac_request.limit = value

    @property
    def mission_enum(self):
        return self.stac_request.mission_enum

    @mission_enum.setter
    def mission_enum(self, value: enum.Mission):
        self.stac_request.mission_enum = value

    @property
    def mosaic_name(self):
        if self.stac_request.HasField("mosaic"):
            return self.stac_request.mosaic.name
        return None

    @mosaic_name.setter
    def mosaic_name(self, value):
        if not self.stac_request.HasField("mosaic"):
            self.stac_request.mosaic.CopyFrom(MosaicRequest(name=value))
        else:
            self.stac_request.mosaic.name = value

    @property
    def offset(self):
        return self.stac_request.offset

    @offset.setter
    def offset(self, value: int):
        self.stac_request.offset = value

    @property
    def platform_enum(self):
        return self.stac_request.platform_enum

    @platform_enum.setter
    def platform_enum(self, value: enum.Platform):
        self.stac_request.platform_enum = value

    @property
    def mosaic_quad_key(self):
        """
Overview of :func:`~StacItemWrap.mosaic_quad_key`

The quad_key to search for mosaic quad STAC items by. If a quad STAC item exists with the key '02313012030231' and this
'mosaic_quad_key' is set to the key of a smaller internal quad, like '02313012030231300', '02313012030231301',
'023130120302313', etc, then the aforementioned '02313012030231' STAC item will be returned.

If a 'mosaic_quad_key' is set to a larger quad, like '02313012030', then the '02313012030231' quad STAC item and many
other quad STAC items that are contained by '02313012030' are returned.
        :return:
        """
        if self.stac_request.HasField("mosaic"):
            return self.stac_request.mosaic.quad_key
        return None

    @mosaic_quad_key.setter
    def mosaic_quad_key(self, value):
        if not self.stac_request.HasField("mosaic"):
            self.stac_request.mosaic.CopyFrom(MosaicRequest(quad_key=value))
        else:
            self.stac_request.mosaic.quad_key = value

    @property
    def stac_request(self):
        return self._stac_data

    def set_bounds(self, bounds: Tuple[float, float, float, float], epsg: int = 0, proj4: str = ""):
        proj = ProjectionData(proj4=proj4)
        if epsg > 0:
            proj = ProjectionData(epsg=epsg)

        bbox = EnvelopeData(xmin=bounds[0], ymin=bounds[1], xmax=bounds[2], ymax=bounds[3], proj=proj)
        self.bbox = bbox

    def set_azimuth(self,
                    rel_type: enum.FilterRelationship,
                    value: float,
                    start: float = None,
                    end: float = None,
                    sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED):
        if not self.stac_request.HasField("view"):
            self.stac_request.view.CopyFrom(ViewRequest())

        float_filter = self._float_filter(rel_type, value, start, end, sort_direction)
        self.stac_request.view.azimuth.CopyFrom(float_filter)

    def set_off_nadir(self,
                      rel_type: enum.FilterRelationship,
                      value: float,
                      start: float = None,
                      end: float = None,
                      sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED):
        if not self.stac_request.HasField("view"):
            self.stac_request.view.CopyFrom(ViewRequest())

        float_filter = self._float_filter(rel_type, value, start, end, sort_direction)
        self.stac_request.view.off_nadir.CopyFrom(float_filter)

    def set_sun_azimuth(self,
                        rel_type: enum.FilterRelationship,
                        value: float,
                        start: float = None,
                        end: float = None,
                        sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED):
        if not self.stac_request.HasField("view"):
            self.stac_request.view.CopyFrom(ViewRequest())

        float_filter = self._float_filter(rel_type, value, start, end, sort_direction)
        self.stac_request.view.sun_azimuth.CopyFrom(float_filter)

    def set_sun_elevation(self,
                          rel_type: enum.FilterRelationship,
                          value: float,
                          start: float = None,
                          end: float = None,
                          sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED):
        if not self.stac_request.HasField("view"):
            self.stac_request.view.CopyFrom(ViewRequest())

        float_filter = self._float_filter(rel_type, value, start, end, sort_direction)
        self.stac_request.view.sun_elevation.CopyFrom(float_filter)

    def set_cloud_cover(self,
                        rel_type: enum.FilterRelationship,
                        value: float = None,
                        start: float = None,
                        end: float = None,
                        sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED):
        if not self.stac_request.HasField("eo"):
            self.stac_request.eo.CopyFrom(EoRequest())

        float_filter = self._float_filter(rel_type, value, start, end, sort_direction)
        self.stac_request.eo.cloud_cover.CopyFrom(float_filter)

    def set_gsd(self,
                rel_type: enum.FilterRelationship,
                value: float,
                start: float = None,
                end: float = None,
                sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED):
        float_filter = self._float_filter(rel_type, value, start, end, sort_direction)
        self.stac_request.gsd.CopyFrom(float_filter)

    def set_observed(self,
                     rel_type: enum.FilterRelationship,
                     value: Union[internal_datetime, date] = None,
                     start: Union[internal_datetime, date] = None,
                     end: Union[internal_datetime, date] = None,
                     sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED,
                     tzinfo: timezone = timezone.utc):
        self._stac_data.observed.CopyFrom(utils.pb_timestampfield(rel_type=rel_type,
                                                                  value=value,
                                                                  start=start,
                                                                  end=end,
                                                                  sort_direction=sort_direction,
                                                                  tzinfo=tzinfo))

    def set_created(self,
                    rel_type: enum.FilterRelationship,
                    value: Union[internal_datetime, date] = None,
                    start: Union[internal_datetime, date] = None,
                    end: Union[internal_datetime, date] = None,
                    sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED,
                    tzinfo: timezone = timezone.utc):
        self._stac_data.created.CopyFrom(utils.pb_timestampfield(rel_type=rel_type,
                                                                 value=value,
                                                                 start=start,
                                                                 end=end,
                                                                 sort_direction=sort_direction,
                                                                 tzinfo=tzinfo))

    def set_updated(self,
                    rel_type: enum.FilterRelationship,
                    value: Union[internal_datetime, date] = None,
                    start: Union[internal_datetime, date] = None,
                    end: Union[internal_datetime, date] = None,
                    sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED,
                    tzinfo: timezone = timezone.utc):
        self._stac_data.updated.CopyFrom(utils.pb_timestampfield(rel_type=rel_type,
                                                                 value=value,
                                                                 start=start,
                                                                 end=end,
                                                                 sort_direction=sort_direction,
                                                                 tzinfo=tzinfo))

    def _float_filter(self,
                      rel_type: enum.FilterRelationship,
                      value: float = None,
                      start: float = None,
                      end: float = None,
                      sort_direction: enum.SortDirection = enum.SortDirection.NOT_SORTED):
        if value is not None:
            if start is not None or end is not None:
                raise ValueError("if value is defined, start and end cannot be used")
            elif rel_type == enum.FilterRelationship.BETWEEN or rel_type == enum.FilterRelationship.NOT_BETWEEN:
                raise ValueError("BETWEEN and NOT_BETWEEN cannot be used with value")
        else:
            if start is None or end is None:
                raise ValueError("if start is defined, end must be defined and vice versa")
            elif rel_type != enum.FilterRelationship.BETWEEN and rel_type != enum.FilterRelationship.NOT_BETWEEN:
                raise ValueError("start + end must be used with BETWEEN or NOT_BETWEEN")
        if rel_type in utils.UNSUPPORTED_TIME_FILTERS:
            raise ValueError("currently not supporting filter {}".format(rel_type.name))

        float_filter = FloatFilter(rel_type=rel_type,
                                   value=value,
                                   start=start,
                                   end=end,
                                   sort_direction=sort_direction)
        return float_filter


class NSLClientEx(NSLClient):
    def __init__(self, nsl_only=False):
        super().__init__(nsl_only=nsl_only)
        self._internal_stac_service = stac_singleton

    def update_service_url(self, stac_service_url):
        """
        update the stac service address
        :param stac_service_url: localhost:8080, 34.34.34.34:9000, http://demo.nearspacelabs.com, etc
        :return:
        """
        super().update_service_url(stac_service_url)
        self._internal_stac_service.update_service_url(stac_service_url=stac_service_url)

    def search_ex(self, stac_request_wrapped: StacRequestWrap, timeout=15) -> Iterator[StacItemWrap]:
        for stac_item in self.search(stac_request_wrapped.stac_request, timeout=timeout):
            if not stac_item.id:
                yield None
            else:
                yield StacItemWrap(stac_item=stac_item)

    def search_one_ex(self, stac_request_wrapped: StacRequestWrap, timeout=15) -> Union[StacItemWrap, None]:
        stac_item = self.search_one(stac_request=stac_request_wrapped.stac_request, timeout=timeout)
        if not stac_item.id:
            return None
        return StacItemWrap(stac_item=stac_item)

    def count_ex(self, stac_request_wrapped: StacRequestWrap, timeout=15) -> int:
        return self.count(stac_request=stac_request_wrapped.stac_request, timeout=timeout)
