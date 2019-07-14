from typing import List
from epl.protobuf import stac_pb2
from epl.protobuf.stac_pb2 import StacItem, AssetType, Eo, CloudPlatform, Asset

DEFAULT_RGB = [Eo.RED, Eo.GREEN, Eo.BLUE]
RASTER_TYPES = (stac_pb2.CO_GEOTIFF, stac_pb2.GEOTIFF, stac_pb2.MRF)


def get_asset(stac_item: StacItem,
              band: Eo.Band,
              asset_types: List[stac_pb2.AssetType] = RASTER_TYPES,
              cloud_platform: CloudPlatform = stac_pb2.UNKNOWN_CLOUD_PLATFORM) -> stac_pb2.Asset:
    for asset_type in asset_types:
        for key in stac_item.assets:
            asset = stac_item.assets[key]
            if asset.asset_type != asset_type:
                continue
            if asset.eo_bands == band:
                if cloud_platform == stac_pb2.UNKNOWN_CLOUD_PLATFORM:
                    return asset
                elif asset.cloud_platform == cloud_platform:
                    return asset

    return None


def has_asset_type(stac_item: StacItem,
                   asset_type: AssetType):
    for key in stac_item.assets:
        asset = stac_item.assets[key]
        if asset.asset_type == asset_type:
            return True
    return False


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

        if asset.cloud_platform == stac_pb2.GCP:
            prefix = prefix.format("gs")
        elif asset.cloud_platform == stac_pb2.AWS:
            prefix = prefix.format("s3")
        else:
            raise ValueError("The only current cloud platforms are GCP and AWS. This asset doesn't have the "
                             "'cloud_platform' field defined")

    return "{0}/{1}/{2}".format(prefix, asset.bucket, asset.object_path)
