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

import base64
import os
import datetime
import http.client
import re
from urllib.parse import urlparse
from typing import List, IO, Union, Dict, Any, Optional
from warnings import warn

import boto3
import botocore
import botocore.exceptions
import botocore.client
from google.cloud import storage
from google.protobuf import timestamp_pb2, duration_pb2

from nsl.stac import gcs_storage_client, bearer_auth, \
    StacItem, StacRequest, Asset, TimestampFilter, Eo, DatetimeRange, enum
from nsl.stac.enum import Band, CloudPlatform, FilterRelationship, SortDirection, AssetType

DEFAULT_RGB = [Band.RED, Band.GREEN, Band.BLUE, Band.NIR]
RASTER_TYPES = [AssetType.CO_GEOTIFF, AssetType.GEOTIFF, AssetType.MRF]
UNSUPPORTED_TIME_FILTERS = [FilterRelationship.IN,
                            FilterRelationship.NOT_IN,
                            FilterRelationship.LIKE,
                            FilterRelationship.NOT_LIKE]


def get_blob_metadata(bucket: str, blob_name: str) -> storage.Blob:
    """
    get metadata/interface for one asset in google cloud storage
    :param bucket: bucket name
    :param blob_name: complete blob name of item (doesn't include bucket name)
    :return: Blob interface item
    """
    if gcs_storage_client.client is None:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

    bucket = gcs_storage_client.client.get_bucket(bucket)
    return bucket.get_blob(blob_name=blob_name.strip('/'))


def download_gcs_object(bucket: str,
                        blob_name: str,
                        file_obj: IO[bytes] = None,
                        save_filename: str = "",
                        make_dir=True) -> str:
    """
    download a specific blob from Google Cloud Storage (GCS) to a file object handle
    :param make_dir: if directory doesn't exist create
    :param bucket: bucket name
    :param blob_name: the full prefix to a specific asset in GCS. Does not include bucket name
    :param file_obj: file object (or BytesIO string_buffer) where data should be written
    :param save_filename: the filename to save the file to
    :return: returns path to downloaded file if applicable
    """
    if make_dir and save_filename != "":
        path_to_create = os.path.split(save_filename)[0]
        if not os.path.exists(path_to_create):
            os.makedirs(path_to_create, exist_ok=True)

    blob = get_blob_metadata(bucket=bucket, blob_name=blob_name)

    if file_obj is not None:
        blob.download_to_file(file_obj=file_obj, client=gcs_storage_client.client)
        if "name" in file_obj.__dict__:
            save_filename = file_obj.name
        else:
            save_filename = ""
        try:
            file_obj.seek(0)
        except:
            pass

        return save_filename
    elif len(save_filename) > 0:
        with open(save_filename, "w+b") as file_obj:
            download_gcs_object(bucket, blob_name, file_obj=file_obj)
        return save_filename
    else:
        raise ValueError("must provide filename or file_obj")


def download_s3_object(bucket: str,
                       blob_name: str,
                       file_obj: IO = None,
                       save_filename: str = "",
                       requester_pays: bool = False) -> str:
    extra_args = None
    if requester_pays:
        extra_args = {'RequestPayer': 'requester'}

    s3 = boto3.client('s3')
    try:
        if file_obj is not None:
            s3.download_fileobj(Bucket=bucket, Key=blob_name, Fileobj=file_obj, ExtraArgs=extra_args)
            if "name" in file_obj.__dict__:
                save_filename = file_obj.name
            else:
                save_filename = ""
            file_obj.seek(0)

            return save_filename
        elif len(save_filename) > 0:
            s3.download_file(Bucket=bucket, Key=blob_name, Filename=save_filename, ExtraArgs=extra_args)
            return save_filename
        else:
            raise ValueError("must provide filename or file_obj")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise


def download_href_object(asset: Asset,
                         file_obj: IO = None,
                         save_filename: str = "",
                         nsl_id: str = None,
                         profile_name: str = None) -> str:
    """
    download the href of an asset
    :param asset: The asset to download
    :param file_obj: BinaryIO file object to download data into. If file_obj and save_filename and/or save_directory
    are set, then only file_obj is used
    :param save_filename: absolute or relative path filename to save asset to (must have write permissions)
    :param nsl_id: ADVANCED ONLY. Only necessary if more than one NSL_ID and NSL_SECRET have been defined with
        set_credentials method. Specify NSL_ID to use for downloading. If NSL_ID and NSL_SECRET environment variables
        are not set, you must use `NSLClient.set_credentials` to add at least one set of credentials.
    :param profile_name: ADVANCED ONLY. Only necessary if more than one NSL profile has been defined with the
        `set_credentials` method. Specifies which NSL profile to use for downloading.
    :return: returns the save_filename. if BinaryIO is not a FileIO object type, save_filename returned is an
    empty string
    """
    if not asset.href:
        raise ValueError("no href on asset")

    host = urlparse(asset.href)
    conn = http.client.HTTPConnection(host.netloc)

    headers = {}
    asset_url = host.path
    if asset.bucket_manager == "Near Space Labs":
        headers = {"authorization": bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)}
        asset_url = "/download/{object}".format(object=asset.object_path)

    if len(asset.type) > 0:
        headers["content-type"] = asset.type
    conn.request(method="GET", url=asset_url, headers=headers)

    res = conn.getresponse()
    if res.status == 404:
        raise ValueError("not found error for {path}".format(path=asset.href))
    elif res.status == 403:
        raise ValueError("auth error for asset {asset}".format(asset=asset.href))
    elif res.status == 402:
        raise ValueError("not enough credits for downloading asset {asset}".format(asset=asset.href))
    elif res.status != 200:
        raise ValueError("error code {code} for asset: {asset}".format(code=res.status, asset=asset.href))

    if len(save_filename) > 0:
        with open(save_filename, mode='wb') as f:
            f.write(res.read())
    elif file_obj is not None:
        file_obj.write(res.read())
        if "name" in file_obj.__dict__:
            save_filename = file_obj.name
        else:
            save_filename = ""
        file_obj.seek(0)
    else:
        raise ValueError("must provide filename or file_obj")

    return save_filename


def download_asset(asset: Asset,
                   from_bucket: bool = False,
                   file_obj: IO[Union[Union[str, bytes], Any]] = None,
                   save_filename: str = "",
                   save_directory: str = "",
                   requester_pays: bool = False,
                   nsl_id: str = None,
                   profile_name: str = None) -> str:
    """
    download an asset. Defaults to downloading from cloud storage. save the data to a BinaryIO file object, a filename
    on your filesystem, or to a directory on your filesystem (the filename will be chosen from the basename of the
    object).
    :param requester_pays: authorize a requester pays download. this can be costly,
    so only enable it if you understand the implications.
    :param asset: The asset to download
    :param from_bucket: force the download to occur from cloud storage instead of href endpoint
    :param file_obj: BinaryIO file object to download data into. If file_obj and save_filename and/or save_directory are
     set, then only file_obj is used
    :param save_filename: absolute or relative path filename to save asset to (must have write permissions)
    :param save_directory: absolute or relative directory path to save asset in (must have write permissions). Filename
    is derived from the basename of the object_path or the href
    :param nsl_id: ADVANCED ONLY. Only necessary if more than one NSL_ID and NSL_SECRET have been defined with
        set_credentials method. Specify NSL_ID to use for downloading. If NSL_ID and NSL_SECRET environment variables
        are not set, you must use `NSLClient.set_credentials` to add at least one set of credentials.
    :param profile_name: ADVANCED ONLY. Only necessary if more than one NSL profile has been defined with the
        `set_credentials` method. Specifies which NSL profile to use for downloading.
    :return:
    """
    if len(save_directory) > 0 and file_obj is None and len(save_filename) == 0:
        if os.path.exists(save_directory):
            save_filename = os.path.join(save_directory, os.path.basename(asset.object_path))
        else:
            raise ValueError("directory 'save_directory' doesn't exist")

    if from_bucket and asset.cloud_platform == CloudPlatform.GCP:
        return download_gcs_object(bucket=asset.bucket,
                                   blob_name=asset.object_path,
                                   file_obj=file_obj,
                                   save_filename=save_filename)
    elif from_bucket and asset.cloud_platform == CloudPlatform.AWS:
        return download_s3_object(bucket=asset.bucket,
                                  blob_name=asset.object_path,
                                  file_obj=file_obj,
                                  save_filename=save_filename,
                                  requester_pays=requester_pays)
    else:
        return download_href_object(asset=asset,
                                    file_obj=file_obj,
                                    save_filename=save_filename,
                                    nsl_id=nsl_id,
                                    profile_name=profile_name)


def download_assets(stac_item: StacItem,
                    save_directory: str,
                    from_bucket: bool = False,
                    nsl_id: str = None) -> List[str]:
    """
    Download all the assets for a StacItem into a directory
    :param nsl_id: ADVANCED ONLY. Only necessary if more than one nsl_id and nsl_secret have been defined with
    set_credentials method.  Specify nsl_id to use. if NSL_ID and NSL_SECRET environment variables not set must use
        NSLClient object's set_credentials to set credentials
    :param stac_item: StacItem containing assets to download
    :param save_directory: the directory where the files should be downloaded
    :param from_bucket: force download from bucket. if set to false downloads happen from href. defaults to False
    :return:
    """
    filenames = []
    for asset_key in stac_item.assets:
        asset = stac_item.assets[asset_key]
        filenames.append(download_asset(asset=asset,
                                        from_bucket=from_bucket,
                                        save_directory=save_directory,
                                        nsl_id=nsl_id))
    return filenames


# TODO https://pypi.org/project/Deprecated/
def get_asset(stac_item: StacItem,
              asset_type: AssetType = None,
              cloud_platform: CloudPlatform = CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
              eo_bands: Eo.Band = Eo.UNKNOWN_BAND,
              asset_regex: Dict = None,
              asset_key: str = None,
              b_relaxed_types: bool = False) -> Optional[Asset]:
    """
    get a protobuf object(pb) asset from a stac item pb. If your parameters are broad (say, if you used all defaults)
    this function would only return you the first asset that matches the parameters. use
    :func:`get_assets <st.stac.utils.get_assets>` to return more than one asset from a request.
    :param stac_item: stac item whose assets we want to search by parameters
    :param asset_type: an asset_type enum to return. if not defined then it is assumed to search all asset types
    :param cloud_platform: only return assets that are hosted on the cloud platform described in the cloud_platform
    field of the item. default grabs the first asset that meets all the other parameters.
    :param band: if the data has electro-optical spectrum data, define the band you want to retrieve. if the data is
    not electro-optical then don't define this parameter (defaults to UNKNOWN_BAND)
    :param asset_basename: only return asset if the basename of the object path matches this value
    :return: asset pb object
    """
    results = get_assets(stac_item, asset_type, cloud_platform, eo_bands, asset_regex, asset_key, b_relaxed_types)
    if len(results) > 1:
        raise ValueError("must be more specific in selecting your asset. if all enums are used, try using "
                         "asset_key_regex")
    elif len(results) == 1:
        return results[0]
    return None


def _asset_types_match(desired_type: enum.AssetType,
                       asset_type: enum.AssetType,
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


def equals_pb(left: Asset, right: Asset):
    """
does the AssetWrap equal a protobuf Asset
    :param other:
    :return:
    """
    return left.SerializeToString() == right.SerializeToString()


# TODO https://pypi.org/project/Deprecated/
def get_assets(stac_item: StacItem,
               asset_type: enum.AssetType = None,
               cloud_platform: CloudPlatform = CloudPlatform.UNKNOWN_CLOUD_PLATFORM,
               eo_bands: Eo.Band = Eo.UNKNOWN_BAND,
               asset_regex: Dict = None,
               asset_key: str = None,
               b_relaxed_types: bool = False) -> List[Asset]:
    """
    get a generator of assets from a stac item, filtered by the parameters.
    :param stac_item: stac item whose assets we want to search by parameters
    :param band: if the data has electro optical spectrum data, define the band you want to retrieve. if the data is not
     electro optical then don't define this parameter (defaults to UNKNOWN_BAND)
    :param asset_types: a list of asset_types to seach. if not defined then it is assumed to search all asset types
    :param cloud_platform: only return assets that are hosted on the cloud platform described in the cloud_platform
    field of the item. default grabs the first asset that meets all the other parameters.
    :param asset_basename: only return asset if the basename of the object path matches this value
    :return: asset pb object
    """
    if asset_key is not None and asset_key in stac_item.assets:
        return [stac_item.assets[asset_key]]
    elif asset_key is not None and asset_key and asset_key not in stac_item.assets:
        raise ValueError("asset_key {} not found".format(asset_key))

    results = []
    for asset_key in stac_item.assets:
        current = stac_item.assets[asset_key]
        b_asset_type_match = _asset_types_match(desired_type=asset_type,
                                                asset_type=current.asset_type,
                                                b_relaxed_types=b_relaxed_types)
        if (eo_bands is not None and eo_bands != enum.Band.UNKNOWN_BAND) and \
                current.eo_bands != eo_bands:
            continue
        if (cloud_platform is not None and cloud_platform != enum.CloudPlatform.UNKNOWN_CLOUD_PLATFORM) and \
                current.cloud_platform != cloud_platform:
            continue
        if (asset_type is not None and asset_type != enum.AssetType.UNKNOWN_ASSET) and \
                not b_asset_type_match:
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
        pb_asset = stac_item.assets[asset_key]
        if not equals_pb(current, pb_asset):
            raise ValueError("corrupted protobuf. Asset and AssetWrap have differing underlying protobuf")

        results.append(current)
    return results


def _asset_has_filename(asset: Asset, asset_basename):
    if os.path.basename(asset.object_path).lower() == os.path.basename(asset_basename).lower():
        return True
    return False


# TODO https://pypi.org/project/Deprecated/
def has_asset_type(stac_item: StacItem, asset_type: AssetType):
    """
    does the stac item contain the asset
    :param stac_item:
    :param asset_type:
    :return:
    """
    for asset in stac_item.assets.values():
        if asset.asset_type == asset_type:
            return True
    return False


# TODO https://pypi.org/project/Deprecated/
def has_asset(stac_item: StacItem, asset: Asset):
    """
    check whether a stac_item has a perfect match to the provided asset
    :param stac_item: stac item whose assets we're checking against asset
    :param asset: asset we're looking for in stac_item
    :return:
    """
    for test_asset in stac_item.assets.values():
        b_matches = True
        for field in test_asset.DESCRIPTOR.fields:
            if getattr(test_asset, field.name) != getattr(asset, field.name):
                b_matches = False
                break
        if b_matches:
            return b_matches
    return False


def item_region(stac_item: StacItem) -> str:
    for asset_key in stac_item.assets:
        return stac_item.assets[asset_key].object_path.split('/')[2]
    warn(f"failed to find STAC item's region: {stac_item.id}")
    return ""


def get_uri(asset: Asset, b_vsi_uri=True, prefix: str = "") -> str:
    """
    construct the uri for the resource in the asset.
    :param asset:
    :param b_vsi_uri:
    :param prefix:
    :return:
    """

    if not asset.bucket or not asset.object_path:
        if not b_vsi_uri:
            raise FileNotFoundError("The bucket ref is not AWS or Google:\nhref : {0}".format(asset.href))
        return '/vsicurl_streaming/{}'.format(asset.href)
    elif not prefix:
        prefix = "{0}://"
        if b_vsi_uri:
            prefix = "/vsi{0}_streaming"

        if asset.cloud_platform == CloudPlatform.GCP:
            prefix = prefix.format("gs")
        elif asset.cloud_platform == CloudPlatform.AWS:
            prefix = prefix.format("s3")
        else:
            raise ValueError("The only current cloud platforms are GCP and AWS. This asset doesn't have the "
                             "'cloud_platform' field defined")

    return "{0}/{1}/{2}".format(prefix, asset.bucket, asset.object_path)


def pb_timestampfield(rel_type: FilterRelationship,
                      value: Union[datetime.datetime, datetime.date] = None,
                      start: Union[datetime.datetime, datetime.date] = None,
                      end: Union[datetime.datetime, datetime.date] = None,
                      sort_direction: SortDirection = SortDirection.NOT_SORTED,
                      tzinfo: datetime.timezone = datetime.timezone.utc) -> TimestampFilter:
    """
    Create a protobuf query filter for a timestamp or a range of timestamps. If you use a datetime.date as
    the value combined with a rel_type of EQ then you will be creating a query filter for the
    24 period of that date.
    :param rel_type: the relationship type to query more
    [here](https://geo-grpc.github.io/api/#epl.protobuf.FieldRelationship)
    :param value: time to search by using >, >=, <, <=, etc. cannot be used with start or end
    :param start: start time for between/not between query. cannot be used with value
    :param end: end time for between/not between query. cannot be used with value
    :param sort_direction: sort direction for results. Defaults to not sorting by this field
    :param tzinfo: timezone info, defaults to UTC
    :return: TimestampFilter
    """
    if rel_type in UNSUPPORTED_TIME_FILTERS:
        raise ValueError("unsupported relationship type: {}".format(rel_type.name))

    if value is not None and rel_type != FilterRelationship.EQ and rel_type != FilterRelationship.NEQ:
        if not isinstance(value, datetime.datetime):
            if rel_type == FilterRelationship.GTE or rel_type == FilterRelationship.LT:
                return TimestampFilter(value=pb_timestamp(value, tzinfo, b_force_min=True),
                                       rel_type=rel_type,
                                       sort_direction=sort_direction)
            elif rel_type == FilterRelationship.LTE or rel_type == FilterRelationship.GT:
                return TimestampFilter(value=pb_timestamp(value, tzinfo, b_force_min=False),
                                       rel_type=rel_type,
                                       sort_direction=sort_direction)
        return TimestampFilter(value=pb_timestamp(value, tzinfo), rel_type=rel_type, sort_direction=sort_direction)
    elif value is not None and not isinstance(value, datetime.datetime) and \
            (rel_type == FilterRelationship.EQ or rel_type == FilterRelationship.NEQ):
        start = datetime.datetime.combine(value, datetime.datetime.min.time(), tzinfo=tzinfo)
        end = datetime.datetime.combine(value, datetime.datetime.max.time(), tzinfo=tzinfo)
        if rel_type == FilterRelationship.EQ:
            rel_type = FilterRelationship.BETWEEN
        else:
            rel_type = FilterRelationship.NOT_BETWEEN

    return TimestampFilter(start=pb_timestamp(start, tzinfo),
                           end=pb_timestamp(end, tzinfo),
                           rel_type=rel_type,
                           sort_direction=sort_direction)


def pb_timestamp(d_utc: Union[datetime.datetime, datetime.date],
                 tzinfo: datetime.timezone = datetime.timezone.utc,
                 b_force_min=True) -> timestamp_pb2.Timestamp:
    """
    create a google.protobuf.Timestamp from a python datetime
    :param d_utc: python datetime or date
    :param tzinfo:
    :return:
    """
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(timezoned(d_utc, tzinfo, b_force_min))
    return ts


def datetime_from_pb_timestamp(ts: timestamp_pb2.Timestamp) -> datetime:
    return datetime.datetime.fromtimestamp(ts.seconds + ts.nanos/1e9)


def timezoned(d_utc: Union[datetime.datetime, datetime.date],
              tzinfo: datetime.timezone = datetime.timezone.utc,
              b_force_min=True) -> datetime.datetime:
    # datetime is child to datetime.date, so if we reverse the order of this instance of we fail
    if isinstance(d_utc, datetime.datetime) and d_utc.tzinfo is None:
        # TODO add warning here:
        # print("warning, no timezone provided with datetime, so UTC is assumed")
        d_utc = datetime.datetime(d_utc.year,
                                  d_utc.month,
                                  d_utc.day,
                                  d_utc.hour,
                                  d_utc.minute,
                                  d_utc.second,
                                  d_utc.microsecond,
                                  tzinfo=tzinfo)
    elif not isinstance(d_utc, datetime.datetime):
        # print("warning, no timezone provided with date, so UTC is assumed")
        if b_force_min:
            d_utc = datetime.datetime.combine(d_utc, datetime.datetime.min.time(), tzinfo=tzinfo)
        else:
            d_utc = datetime.datetime.combine(d_utc, datetime.datetime.max.time(), tzinfo=tzinfo)
    return d_utc


# TODO https://pypi.org/project/Deprecated/
def duration(d_start: Union[datetime.datetime, datetime.date], d_end: Union[datetime.datetime, datetime.date]):
    d = duration_pb2.Duration()
    d.FromTimedelta(timezoned(d_end) - timezoned(d_start))
    return d


# TODO https://pypi.org/project/Deprecated/
def datetime_range(d_start: Union[datetime.datetime, datetime.date],
                   d_end: Union[datetime.datetime, datetime.date]) -> DatetimeRange:
    """
    for datetime range definitions for Mosaic objects.
    :param d_start: start datetime or date
    :param d_end: end datetime or date
    :return: DatetimeRange object
    """
    return DatetimeRange(start=pb_timestamp(d_start), end=pb_timestamp(d_end))


def stac_request_to_b64(req: StacRequest) -> str:
    return str(base64.b64encode(req.SerializeToString()), encoding='ascii')


def stac_request_from_b64(encoded: str) -> StacRequest:
    req = StacRequest()
    req.ParseFromString(base64.b64decode(bytes(encoded, encoding='ascii')))
    return req
