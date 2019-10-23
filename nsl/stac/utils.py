import os
import datetime

import boto3
import botocore

from typing import List, Iterator, BinaryIO

from google.cloud import storage
from google.protobuf import timestamp_pb2, duration_pb2
from epl.protobuf import stac_pb2

from nsl.stac import storage_client

DEFAULT_RGB = [stac_pb2.Eo.RED, stac_pb2.Eo.GREEN, stac_pb2.Eo.BLUE]
RASTER_TYPES = [stac_pb2.CO_GEOTIFF, stac_pb2.GEOTIFF, stac_pb2.MRF]


def _gcp_blob_metadata(bucket: str, blob_name: str) -> storage.Blob:
    """
    get metadata/interface for one asset in google cloud storage
    :param bucket: bucket name
    :param blob_name: complete blob name of item (doesn't include bucket name)
    :return: Blob interface item
    """
    bucket = storage_client.get_bucket(bucket)
    return bucket.get_blob(blob_name=blob_name.strip('/'))


def _download_gcp_file(bucket: str,
                       blob_name: str,
                       file_obj: BinaryIO = None,
                       save_filename: str = "") -> str:
    """
    download a specific blob from Google Cloud Storage (GCS) to a file object handle
    :param bucket: bucket name
    :param blob_name: the full prefix to a specific asset in GCS. Does not include bucket name
    :param file_obj: file object (or BytesIO string_buffer) where data should be written
    :return: returns path to downloaded file if applicable
    """
    blob = _gcp_blob_metadata(bucket=bucket, blob_name=blob_name)

    if file_obj is not None:
        result = file_obj.name
        blob.download_to_file(file_obj=file_obj, client=storage_client)
        file_obj.seek(0)

        return result
    elif len(save_filename) > 0:
        blob.download_to_filename(filename=save_filename, client=storage_client)
        return save_filename
    else:
        raise ValueError("must provide filename or file_obj")


def _download_aws_bucket_item(bucket: str,
                              blob_name: str,
                              file_obj: BinaryIO = None,
                              save_filename: str = ""):
    # TODO, can this be global?
    s3 = boto3.resource('s3')
    try:
        bucket_obj = s3.Bucket(bucket)
        if file_obj is not None:
            result = file_obj.name
            bucket_obj .download_fileobj(blob_name, file_obj)
            file_obj.seek(0)

            return result
        elif len(save_filename) > 0:
            bucket_obj.download_file(blob_name, save_filename)
            return save_filename
        else:
            raise ValueError("must provide filename or file_obj")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise


def download_asset(asset: stac_pb2.Asset,
                   b_from_bucket: bool = True,
                   file_obj: BinaryIO = None,
                   save_filename: str = "",
                   save_directory: str = ""):
    if file_obj is not None and (len(save_filename) > 0 or len(save_directory) > 0):
        raise ValueError("either file_obj, save_filename or save_directory must be defined")
    elif len(save_directory):
        if os.path.exists(save_directory):
            save_filename = os.path.join(save_directory, os.path.basename(asset.object_path))
        else:
            raise ValueError("directory 'save_directory' doesn't exist")

    if b_from_bucket and asset.cloud_platform == stac_pb2.GCP:
        return _download_gcp_file(bucket=asset.bucket,
                                  blob_name=asset.object_path,
                                  file_obj=file_obj,
                                  save_filename=save_filename)
    elif b_from_bucket and asset.cloud_platform == stac_pb2.AWS:
        return _download_aws_bucket_item(bucket=asset.bucket,
                                         blob_name=asset.object_path,
                                         file_obj=file_obj,
                                         save_filename=save_filename)
    else:
        raise ValueError("only GCP bucket downloads supported")


def download_assets(stac_item: stac_pb2.StacItem,
                    b_from_bucket: bool = True,
                    save_directory: str = "") -> List[str]:
    filenames = []
    for asset_key in stac_item.assets:
        asset = stac_item.assets[asset_key]
        filenames.append(download_asset(asset=asset,
                                        b_from_bucket=b_from_bucket,
                                        save_directory=save_directory))
    return filenames


def get_asset(stac_item: stac_pb2.StacItem,
              band: stac_pb2.Eo.Band = stac_pb2.Eo.UNKNOWN_BAND,
              asset_types: List = None,
              cloud_platform: stac_pb2.CloudPlatform = stac_pb2.UNKNOWN_CLOUD_PLATFORM,
              asset_basename: str = "") -> stac_pb2.Asset:
    """
    get protobuf object(pb) asset from a stac item pb.
    :param stac_item: stac item whose assets we want to search by parameters
    :param band: if the data has electro optical spectrum data, define the band you want to retrieve. if the data is
    not electro optical then don't define this parameter (defaults to UNKNOWN_BAND)
    :param asset_types: a list of asset_types to seach. if not defined then it is assumed to search all asset types
    :param cloud_platform: only return assets that are hosted on the cloud platform described in the cloud_platform
    field of the item. default grabs the first asset that meets all the other parameters.
    :param asset_basename: only return asset if the basename of the object path matches this value
    :return: asset pb object
    """
    # return next(get_assets(stac_item, band, asset_types, cloud_platform, asset_basename))
    data = list(get_assets(stac_item, band, asset_types, cloud_platform, asset_basename))
    if len(data) == 0:
        return None
    return data[0]


def get_assets(stac_item: stac_pb2.StacItem,
               band: stac_pb2.Eo.Band = stac_pb2.Eo.UNKNOWN_BAND,
               asset_types: List = None,
               cloud_platform: stac_pb2.CloudPlatform = stac_pb2.UNKNOWN_CLOUD_PLATFORM,
               asset_basename: str = "") -> Iterator[stac_pb2.Asset]:
    """
    get a generator of protobuf object(pb) assets from a stac item pb.
    :param stac_item: stac item whose assets we want to search by parameters
    :param band: if the data has electro optical spectrum data, define the band you want to retrieve. if the data is
    not electro optical then don't define this parameter (defaults to UNKNOWN_BAND)
    :param asset_types: a list of asset_types to seach. if not defined then it is assumed to search all asset types
    :param cloud_platform: only return assets that are hosted on the cloud platform described in the cloud_platform
    field of the item. default grabs the first asset that meets all the other parameters.
    :param asset_basename: only return asset if the basename of the object path matches this value
    :return: asset pb object
    """
    if asset_types is None:
        asset_types = [stac_pb2.AssetType.Value(asset_type_str) for asset_type_str in stac_pb2.AssetType.keys()]

    if not isinstance(asset_types, List):
        asset_types = [asset_types]

    for asset_type in asset_types:
        for key in stac_item.assets:
            asset = stac_item.assets[key]
            if asset.asset_type != asset_type:
                continue
            if asset.eo_bands == band or band == stac_pb2.Eo.UNKNOWN_BAND:
                if asset.cloud_platform == cloud_platform or cloud_platform == stac_pb2.UNKNOWN_CLOUD_PLATFORM:
                    if asset_basename and not _asset_has_filename(asset=asset, asset_basename=asset_basename):
                        continue
                    yield asset

    return


def get_eo_assets(stac_item: stac_pb2.StacItem,
                  cloud_platform: stac_pb2.CloudPlatform = stac_pb2.UNKNOWN_CLOUD_PLATFORM,
                  bands: List = DEFAULT_RGB,
                  asset_types: List = RASTER_TYPES) -> Iterator[stac_pb2.Asset]:
    """
    get generator of electro optical assets that match the restrictions. if no restrictions are set,
    then the default is any cloud platform, RGB for the bands, and all raster types.
    :param stac_item: stac item to search for electro optical assets
    :param cloud_platform: cloud platform (if an asset has both GCP and AWS but you prefer AWS, set this)
    :param bands: the tuple of any of the bands you'd like to return
    :param asset_types: the tuple of any of the asset types you'd like to return
    :return: List of Assets
    """

    if asset_types is None:
        asset_types = RASTER_TYPES

    if cloud_platform is None:
        cloud_platform = stac_pb2.UNKNOWN_CLOUD_PLATFORM

    assets = []
    for band in bands:
        if band == stac_pb2.Eo.RGB or band == stac_pb2.Eo.RGBIR:
            yield get_eo_assets(stac_item=stac_item,
                                bands=DEFAULT_RGB,
                                cloud_platform=cloud_platform,
                                asset_types=asset_types)
            if band == stac_pb2.Eo.RGBIR:
                yield get_assets(stac_item=stac_item,
                                 band=stac_pb2.Eo.NIR,
                                 cloud_platform=cloud_platform,
                                 asset_types=asset_types)
        else:
            yield get_assets(stac_item=stac_item,
                             band=band,
                             cloud_platform=cloud_platform,
                             asset_types=asset_types)

    return assets


def _asset_has_filename(asset: stac_pb2.Asset, asset_basename):
    if os.path.basename(asset.object_path).lower() == os.path.basename(asset_basename).lower():
        return True
    return False


def has_asset_type(stac_item: stac_pb2.StacItem,
                   asset_type: stac_pb2.AssetType):
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


def has_asset(stac_item: stac_pb2.StacItem,
              asset: stac_pb2.Asset):
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


def get_uri(asset: stac_pb2.Asset, b_vsi_uri=True, prefix: str = "") -> str:
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

        if asset.cloud_platform == stac_pb2.GCP:
            prefix = prefix.format("gs")
        elif asset.cloud_platform == stac_pb2.AWS:
            prefix = prefix.format("s3")
        else:
            raise ValueError("The only current cloud platforms are GCP and AWS. This asset doesn't have the "
                             "'cloud_platform' field defined")

    return "{0}/{1}/{2}".format(prefix, asset.bucket, asset.object_path)


def pb_timestamp(d_utc: datetime.datetime or datetime.date) -> timestamp_pb2.Timestamp:
    """
    create a google.protobuf.Timestamp from a python datetime
    :param d_utc: python datetime or date
    :return:
    """
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(timezoned(d_utc))
    return ts


def timezoned(d_utc: datetime.datetime or datetime.date):
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
                                  tzinfo=datetime.timezone.utc)
    elif not isinstance(d_utc, datetime.datetime):
        # print("warning, no timezone provided with date, so UTC is assumed")
        d_utc = datetime.datetime.combine(d_utc, datetime.datetime.min.time(), tzinfo=datetime.timezone.utc)
    return d_utc


def duration(d_start: datetime.date or datetime.datetime, d_end: datetime.date or datetime.datetime):
    d = duration_pb2.Duration()
    d.FromTimedelta(timezoned(d_end) - timezoned(d_start))
    return d
