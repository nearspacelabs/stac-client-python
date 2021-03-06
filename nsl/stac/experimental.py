import pathlib
import re
from copy import deepcopy

import boto3
import botocore.exceptions

from datetime import date, datetime, timezone
from typing import Union, Iterator, List, Optional, Tuple, Dict

from epl.protobuf.v1.geometry_pb2 import ProjectionData
from google.protobuf.any_pb2 import Any
from google.protobuf.wrappers_pb2 import FloatValue
from epl.geometry import BaseGeometry, Polygon
from typing.io import BinaryIO, IO

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


def _check_assets_exist(stac_item: StacItem, b_raise=True) -> List[str]:
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


class AssetWrap(object):
    def __init__(self,
                 asset: Asset = None,
                 bucket: str = None,
                 object_path: str = None,
                 asset_type: enum.AssetType = enum.AssetType.UNKNOWN_ASSET,
                 eo_bands: enum.Band = enum.Band.UNKNOWN_BAND,
                 href="",
                 cloud_platform: enum.CloudPlatform = enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
                 bucket_manager: str = "",
                 bucket_region: str = "",
                 key_suffix: str = "",
                 asset_key: str = ""):
        self._asset_key = asset_key
        if asset is None:
            asset = Asset(href=href,
                          eo_bands=eo_bands,
                          asset_type=asset_type,
                          cloud_platform=cloud_platform,
                          bucket_manager=bucket_manager,
                          bucket_region=bucket_region,
                          bucket=bucket,
                          object_path=object_path)

        self._asset = asset

        if self._asset.bucket is None or self._asset.object_path is None:
            raise ValueError("bucket and object path must be set in valid asset")

        self._ext = pathlib.Path(self._asset.object_path).suffix

        b_thumbnail_png = self._asset.asset_type == enum.AssetType.THUMBNAIL and self._ext == '.png'
        _, href_type = self._asset_type_details(asset_type=self._asset.asset_type, b_thumbnail_png=b_thumbnail_png)
        self._asset.type = href_type
        self._type = href_type
        self._key_suffix = key_suffix

    def __eq__(self, other):
        if not isinstance(other, AssetWrap):
            return False

        if self.asset_key != other.asset_key:
            return False

        return self.equals_pb(other._asset)

    def __str__(self):
        return str("{0}extension: {1}\nasset_key: {2}".format(self._asset, self._ext, self.asset_key))

    def __copy__(self):
        pass

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == '_asset':
                value = Asset()
                value.CopyFrom(v)
                setattr(result, k, value)
            else:
                setattr(result, k, deepcopy(v))
        return result

    def _asset_key_prefix(self) -> str:
        if self.eo_bands == enum.Band.UNKNOWN_BAND:
            return "{0}_{1}".format(self.asset_type.name, self.cloud_platform.name)
        return "{0}_{1}_{2}".format(self.asset_type.name, self.eo_bands.name, self.cloud_platform.name)

    @property
    def asset(self) -> Asset:
        return self._asset

    @property
    def asset_key(self) -> str:
        if self._asset_key:
            return self._asset_key

        asset_key = self._asset_key_prefix()
        if self._key_suffix:
            asset_key += "_{}".format(self._key_suffix)
        return asset_key

    @property
    def asset_key_suffix(self) -> str:
        return self._key_suffix

    @asset_key_suffix.setter
    def asset_key_suffix(self, value: str):
        self._key_suffix = value

    @property
    def asset_type(self) -> enum.AssetType:
        """
type of asset
        :return:
        """
        return enum.AssetType(self._asset.asset_type)

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
        return enum.CloudPlatform(self._asset.cloud_platform)

    @cloud_platform.setter
    def cloud_platform(self, value: enum.CloudPlatform):
        self._asset.cloud_platform = value

    @property
    def eo_bands(self) -> enum.Band:
        """
electro optical bands included in data. if data is not electro optical, then this is set to Unknown
        :return:
        """
        return enum.Band(self._asset.eo_bands)

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

    @href.setter
    def href(self, value: str):
        self._asset.href = value

    @property
    def object_path(self) -> str:
        """
the object path to use with the bucket if access is available
        :return:
        """
        return self._asset.object_path

    @object_path.setter
    def object_path(self, value: str):
        self._asset.object_path = value

    @property
    def type(self) -> str:
        return self._type

    def equals_pb(self, other: Asset):
        """
does the AssetWrap equal a protobuf Asset
        :param other:
        :return:
        """
        return self._asset.SerializeToString() == other.SerializeToString()

    def exists(self) -> bool:
        return _check_asset_exists(self._asset)

    def download(self,
                 from_bucket: bool = False,
                 file_obj: IO[Union[Union[str, bytes], Any]] = None,
                 save_filename: str = '',
                 save_directory: str = '',
                 requester_pays: bool = False,
                 nsl_id: str = None) -> str:
        return utils.download_asset(asset=self._asset,
                                    from_bucket=from_bucket,
                                    file_obj=file_obj,
                                    save_filename=save_filename,
                                    save_directory=save_directory,
                                    requester_pays=requester_pays,
                                    nsl_id=nsl_id)

    @staticmethod
    def _asset_type_details(asset_type: enum.AssetType, b_thumbnail_png: bool = True) -> (str, str):
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

    def __eq__(self, other):
        if not isinstance(other, StacItemWrap):
            return False

        return self.equals_pb(other.stac_item)

    def __init__(self, stac_item: StacItem = None, properties_constructor=None):
        self._assets = {}
        if stac_item is None:
            stac_data = StacItem()
        else:
            stac_data = StacItem()
            stac_data.CopyFrom(stac_item)

            for asset_key in stac_data.assets:
                self._assets[asset_key] = AssetWrap(stac_data.assets[asset_key], asset_key=asset_key)

        super().__init__(stac_data, properties_constructor)
        if self.created is None:
            self.created = datetime.now(tz=timezone.utc)

    def __copy__(self):
        pass

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == '_stac_data':
                value = StacItem()
                value.CopyFrom(v)
                setattr(result, k, value)
            else:
                setattr(result, k, deepcopy(v))
        return result

    @property
    def bbox(self) -> EnvelopeData:
        """
bounding box of data. In form of EnvelopeData
        :return:
        """
        return self.stac_item.bbox

    @property
    def cloud_cover(self) -> Optional[float]:
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
    def constellation(self) -> enum.Constellation:
        """
the enum describing the constellation
        :return:
        """
        return enum.Constellation(self.stac_item.constellation_enum)

    @constellation.setter
    def constellation(self, value: enum.Constellation):
        self.stac_item.constellation_enum = value
        self.stac_item.constellation = self.constellation.name

    @property
    def created(self) -> Optional[datetime]:
        if self.stac_item.HasField("created"):
            return datetime.fromtimestamp(self.stac_item.created.seconds, tz=timezone.utc)
        else:
            return None

    @created.setter
    def created(self, value: Union[datetime, date]):
        self.stac_item.created.CopyFrom(utils.pb_timestamp(d_utc=value))

    @property
    def end_observed(self) -> Optional[datetime]:
        return self.stac_item.end_observed

    @end_observed.setter
    def end_observed(self, value: Union[datetime, date]):
        self.stac_item.end_observation.CopyFrom(utils.pb_timestamp(d_utc=value))
        self.stac_item.end_datetime.CopyFrom(utils.pb_timestamp(d_utc=value))

    @property
    def feature(self):
        """
geojson feature with geometry being only aspect defined
        :return:
        """
        return {
            'type': 'Feature',
            'geometry': self.geometry.__geo_interface__,
            'id': self.id,
            'collection': self.collection,
            'properties': self._feature_properties(),
            'assets': self._feature_assets()
        }

    @staticmethod
    def _append_prop(props: Dict, prop_name: str, prop_value):
        if prop_value is None:
            return props
        if props is None:
            props = {}
        props[prop_name] = prop_value
        return props

    def _feature_properties(self) -> Dict:
        props = {}
        props = StacItemWrap._append_prop(props, 'datetime', self.observed.replace(microsecond=0).isoformat())
        props = StacItemWrap._append_prop(props, 'observed', self.observed.replace(microsecond=0).isoformat())
        props = StacItemWrap._append_prop(props, 'mission', self.mission.name)
        props = StacItemWrap._append_prop(props, 'platform', self.platform.name)
        props = StacItemWrap._append_prop(props, 'instrument', self.instrument.name)
        props = StacItemWrap._append_prop(props, 'gsd', self.gsd)
        props = StacItemWrap._append_prop(props, 'eo:cloud_cover', self.cloud_cover)
        props = StacItemWrap._append_prop(props, 'view:off_nadir', self.off_nadir)
        return props

    def _feature_assets(self) -> Dict:
        feature_assets = {}
        for asset_wrap in self.get_assets():
            feature_assets[asset_wrap.asset_key] = {
                'href': asset_wrap.href,
                'type': asset_wrap.type,
            }
        return feature_assets

    @property
    def geometry(self) -> BaseGeometry:
        if self.stac_item.HasField("geometry"):
            return BaseGeometry.import_protobuf(self.stac_item.geometry)
        elif self.stac_item.HasField("bbox"):
            return Polygon.from_envelope_data(self.stac_item.bbox)

    @geometry.setter
    def geometry(self, value: BaseGeometry):
        self.stac_item.geometry.CopyFrom(value.geometry_data)
        self.stac_item.bbox.CopyFrom(value.envelope_data)

    @property
    def gsd(self) -> Optional[float]:
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
    def id(self) -> str:
        return self.stac_item.id

    @id.setter
    def id(self, value: str):
        self.stac_item.id = value

    @property
    def instrument(self) -> enum.Instrument:
        return enum.Instrument(self.stac_item.instrument_enum)

    @instrument.setter
    def instrument(self, value: enum.Instrument):
        self.stac_item.instrument_enum = value
        self.stac_item.instrument = self.instrument.name

    @property
    def mission(self) -> enum.Mission:
        return enum.Mission(self.stac_item.mission_enum)

    @mission.setter
    def mission(self, value: enum.Mission):
        self.stac_item.mission_enum = value
        self.stac_item.mission = self.mission.name

    @property
    def mosaic_name(self) -> Optional[str]:
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
    def mosaic_quad_key(self) -> Optional[str]:
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
    def observed(self) -> Optional[datetime]:
        if self.stac_item.HasField("datetime"):
            return datetime.fromtimestamp(self.stac_item.datetime.seconds, tz=timezone.utc)
        elif self.stac_item.HasField("observed"):
            return datetime.fromtimestamp(self.stac_item.observed.seconds, tz=timezone.utc)
        else:
            return None

    @observed.setter
    def observed(self, value: Union[datetime, date]):
        self.stac_item.datetime.CopyFrom(utils.pb_timestamp(d_utc=value))
        self.stac_item.observed.CopyFrom(utils.pb_timestamp(d_utc=value))

    @property
    def off_nadir(self) -> Optional[float]:
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
    def platform(self) -> enum.Platform:
        return enum.Platform(self.stac_item.platform_enum)

    @platform.setter
    def platform(self, value: enum.Platform):
        self.stac_item.platform_enum = value
        self.stac_item.platform = self.platform.name

    @property
    def provenance_ids(self) -> List[str]:
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
    def stac_item(self) -> StacItem:
        """
        get stac_item
        :return: StacItem
        """
        return self._stac_data

    @property
    def updated(self) -> Optional[datetime]:
        if self.stac_item.HasField("updated"):
            return datetime.fromtimestamp(self.stac_item.updated.seconds, tz=timezone.utc)
        else:
            return None

    @updated.setter
    def updated(self, value: Union[datetime, date]):
        self.stac_item.updated.CopyFrom(utils.pb_timestamp(d_utc=value))

    def download_asset(self,
                       asset_key: str = "",
                       asset_type: enum.AssetType = enum.AssetType.UNKNOWN_ASSET,
                       cloud_platform: enum.CloudPlatform = enum.CloudPlatform.GCP,
                       eo_bands: enum.Band = enum.Band.UNKNOWN_BAND,
                       asset_key_regex: str = None,
                       from_bucket: bool = False,
                       file_obj: BinaryIO = None,
                       save_filename: str = "",
                       save_directory: str = "") -> str:
        asset_wrap = self.get_asset(asset_key=asset_key,
                                    asset_type=asset_type,
                                    cloud_platform=cloud_platform,
                                    eo_bands=eo_bands,
                                    asset_key_regex=asset_key_regex)

        return asset_wrap.download(from_bucket=from_bucket,
                                   file_obj=file_obj,
                                   save_filename=save_filename,
                                   save_directory=save_directory)

    def equals_pb(self, other: StacItem):
        """
does the StacItemWrap equal a protobuf StacItem
        :param other:
        :return:
        """
        return self.stac_item.SerializeToString() == other.SerializeToString()

    @staticmethod
    def _asset_types_match(desired_type: enum.AssetType, asset_type: enum.AssetType,
                           b_relaxed_types: bool = False) -> bool:
        if not b_relaxed_types:
            return desired_type == asset_type
        elif desired_type == enum.AssetType.TIFF:
            return asset_type == desired_type or \
                   asset_type == enum.AssetType.GEOTIFF or \
                   asset_type == enum.AssetType.CO_GEOTIFF
        elif desired_type == enum.AssetType.GEOTIFF:
            return asset_type == desired_type or asset_type == enum.AssetType.CO_GEOTIFF
        return asset_type == desired_type

    def get_assets(self,
                   asset_key: str = None,
                   asset_type: enum.AssetType = enum.AssetType.UNKNOWN_ASSET,
                   cloud_platform: enum.CloudPlatform = enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
                   eo_bands: enum.Band = enum.Band.UNKNOWN_BAND,
                   asset_regex: Dict = None,
                   b_relaxed_types: bool = False) -> List[AssetWrap]:
        if asset_key is not None and asset_key in self._assets:
            return [self._assets[asset_key]]
        elif asset_key is not None and asset_key and asset_key not in self._assets:
            raise ValueError("asset_key {} not found".format(asset_key))

        results = []
        for asset_key in self._assets:
            current = self._assets[asset_key]
            b_asset_type_match = self._asset_types_match(desired_type=asset_type,
                                                         asset_type=current.asset_type,
                                                         b_relaxed_types=b_relaxed_types)
            if (eo_bands is not None and eo_bands != enum.Band.UNKNOWN_BAND) and current.eo_bands != eo_bands:
                continue
            if (cloud_platform is not None and cloud_platform != enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM) and \
                    current.cloud_platform != cloud_platform:
                continue
            if (asset_type is not None and asset_type != enum.AssetType.UNKNOWN_ASSET) and not b_asset_type_match:
                continue
            if asset_regex is not None and len(asset_regex) > 0:
                b_continue = False
                for key, regex_value in asset_regex.items():
                    if key == 'asset_key':
                        if not re.match(regex_value, asset_key):
                            b_continue = True
                            break
                    else:
                        if not hasattr(current, key):
                            raise AttributeError("no key {0} in asset {1}".format(key, current))
                        elif not re.match(regex_value, getattr(current, key)):
                            b_continue = True
                            break

                if b_continue:
                    continue

            # check that asset hasn't changed between protobuf and asset_map
            pb_asset = self.stac_item.assets[asset_key]
            if not current.equals_pb(pb_asset):
                raise ValueError("corrupted protobuf. Asset and AssetWrap have differing underlying protobuf")

            results.append(current)
        return results

    def get_asset(self,
                  asset_key: str = None,
                  asset_type: enum.AssetType = enum.AssetType.UNKNOWN_ASSET,
                  cloud_platform: enum.CloudPlatform = enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
                  eo_bands: Eo.Band = Eo.UNKNOWN_BAND,
                  asset_regex: Dict = None,
                  b_relaxed_types: bool = False) -> Optional[AssetWrap]:
        results = self.get_assets(asset_key, asset_type, cloud_platform, eo_bands, asset_regex, b_relaxed_types)
        if len(results) > 1:
            raise ValueError("must be more specific in selecting your asset. if all enums are used, try using "
                             "asset_key_regex")
        elif len(results) == 1:
            return results[0]
        return None

    def check_assets_exist(self, b_raise) -> List[str]:
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
    def constellation(self) -> enum.Constellation:
        return enum.Constellation(self.stac_request.constellation_enum)

    @constellation.setter
    def constellation(self, value: enum.Constellation):
        self.stac_request.constellation_enum = value

    @property
    def id(self) -> str:
        return self.stac_request.id

    @id.setter
    def id(self, value: str):
        self.stac_request.id = value

    @property
    def instrument(self) -> enum.Instrument:
        return enum.Instrument(self.stac_request.instrument_enum)

    @instrument.setter
    def instrument(self, value: enum.Instrument):
        self.stac_request.instrument_enum = value

    @property
    def intersects(self) -> Optional[BaseGeometry]:
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
    def limit(self) -> int:
        return self.stac_request.limit

    @limit.setter
    def limit(self, value: int):
        self.stac_request.limit = value

    @property
    def mission(self) -> enum.Mission:
        return enum.Mission(self.stac_request.mission_enum)

    @mission.setter
    def mission(self, value: enum.Mission):
        self.stac_request.mission_enum = value

    @property
    def mosaic_name(self) -> Optional[str]:
        if self.stac_request.HasField("mosaic"):
            return self.stac_request.mosaic.name
        return None

    @mosaic_name.setter
    def mosaic_name(self, value: str):
        if not self.stac_request.HasField("mosaic"):
            self.stac_request.mosaic.CopyFrom(MosaicRequest(name=value))
        else:
            self.stac_request.mosaic.name = value

    @property
    def mosaic_quad_key(self) -> Optional[str]:
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
    def mosaic_quad_key(self, value: str):
        if not self.stac_request.HasField("mosaic"):
            self.stac_request.mosaic.CopyFrom(MosaicRequest(quad_key=value))
        else:
            self.stac_request.mosaic.quad_key = value

    @property
    def offset(self) -> int:
        return self.stac_request.offset

    @offset.setter
    def offset(self, value: int):
        self.stac_request.offset = value

    @property
    def platform(self) -> enum.Platform:
        return enum.Platform(self.stac_request.platform_enum)

    @platform.setter
    def platform(self, value: enum.Platform):
        self.stac_request.platform_enum = value

    @property
    def stac_request(self) -> StacRequest:
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
                     value: Union[datetime, date] = None,
                     start: Union[datetime, date] = None,
                     end: Union[datetime, date] = None,
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
                    value: Union[datetime, date] = None,
                    start: Union[datetime, date] = None,
                    end: Union[datetime, date] = None,
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
                    value: Union[datetime, date] = None,
                    start: Union[datetime, date] = None,
                    end: Union[datetime, date] = None,
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

    def search_ex(self,
                  stac_request_wrapped: StacRequestWrap,
                  timeout=15,
                  nsl_id: str = None,
                  profile_name: str = None,
                  increment_search: Optional[int] = None) -> Iterator[StacItemWrap]:
        if increment_search is not None and increment_search > 0 and stac_request_wrapped.offset > 0:
            raise ValueError("can't use offset and increment_search. offset should be paired with limit, "
                             "and increment_search should be set to None")

        if increment_search is not None and increment_search > stac_request_wrapped.limit:
            # TODO put a warning here?
            increment_search = None

        if increment_search is None or increment_search <= 0:
            for stac_item in list(self.search(stac_request_wrapped.stac_request,
                                              timeout=timeout,
                                              nsl_id=nsl_id,
                                              profile_name=profile_name)):
                if not stac_item.id:
                    return
                else:
                    yield StacItemWrap(stac_item=stac_item)
        else:
            expected_total = stac_request_wrapped.limit
            total = 0
            stac_request_wrapped.limit = increment_search
            stac_request_wrapped.offset = 0
            items = list(self.search(stac_request_wrapped.stac_request,
                                     timeout=timeout,
                                     nsl_id=nsl_id,
                                     profile_name=profile_name))
            while len(items) > 0:
                for stac_item in items:
                    total += 1
                    yield StacItemWrap(stac_item=stac_item)
                    if total >= expected_total:
                        return

                stac_request_wrapped.offset += stac_request_wrapped.limit
                items = list(self.search(stac_request_wrapped.stac_request,
                                         timeout=timeout,
                                         nsl_id=nsl_id,
                                         profile_name=profile_name))

    def feature_collection_ex(self,
                              stac_request_wrapped: StacRequestWrap,
                              timeout=15,
                              nsl_id: str = None,
                              profile_name: str = None,
                              increment_search: int = None,
                              feature_collection: Dict = None) -> Dict:
        if feature_collection is None:
            feature_collection = {'type': 'FeatureCollection', 'features': []}

        items = self.search_ex(stac_request_wrapped,
                               timeout=timeout,
                               nsl_id=nsl_id,
                               profile_name=profile_name,
                               increment_search=increment_search)
        for item in items:
            feature_collection['features'].append(item.feature)

        return feature_collection

    def search_one_ex(self,
                      stac_request_wrapped: StacRequestWrap,
                      timeout=15,
                      nsl_id: str = None,
                      profile_name: str = None) -> Optional[StacItemWrap]:
        stac_item = self.search_one(stac_request=stac_request_wrapped.stac_request,
                                    timeout=timeout, nsl_id=nsl_id, profile_name=profile_name)
        if not stac_item.id:
            return None
        return StacItemWrap(stac_item=stac_item)

    def count_ex(self,
                 stac_request_wrapped: StacRequestWrap,
                 timeout=15,
                 nsl_id: str = None,
                 profile_name: str = None) -> int:
        return self.count(stac_request=stac_request_wrapped.stac_request,
                          timeout=timeout, nsl_id=nsl_id, profile_name=profile_name)
