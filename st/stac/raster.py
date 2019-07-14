from typing import List

from epl.protobuf import stac_pb2

DEFAULT_RGB = [stac_pb2.Eo.RED, stac_pb2.Eo.GREEN, stac_pb2.Eo.BLUE]
RASTER_TYPES = [stac_pb2.CO_GEOTIFF, stac_pb2.GEOTIFF, stac_pb2.MRF]


def get_asset(stac_item: stac_pb2.StacItem,
              cloud_platform: stac_pb2.CloudPlatform,
              band: stac_pb2.Eo.Band,
              asset_types: List = None) -> stac_pb2.Asset:
    if asset_types is None:
        asset_types = RASTER_TYPES

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


def get_assets(stac_item: stac_pb2.StacItem,
               cloud_platform: stac_pb2.CloudPlatform,
               bands: List = None,
               asset_types: List = None) -> List:
    if bands is None:
        bands = DEFAULT_RGB

    if asset_types is None:
        asset_types = RASTER_TYPES

    if cloud_platform is None:
        cloud_platform = stac_pb2.UNKNOWN_CLOUD_PLATFORM

    assets = []
    for band in bands:
        if band == stac_pb2.Eo.RGB or band == stac_pb2.Eo.RGBIR:
            assets.extend(get_assets(stac_item=stac_item, bands=DEFAULT_RGB, cloud_platform=cloud_platform,
                                     asset_types=asset_types))
            if band == stac_pb2.Eo.RGBIR:
                assets.append(get_asset(stac_item=stac_item, band=stac_pb2.Eo.NIR, cloud_platform=cloud_platform,
                                        asset_types=asset_types))
        else:
            assets.append(
                get_asset(stac_item=stac_item, band=band, cloud_platform=cloud_platform, asset_types=asset_types))

    return assets


def has_asset_type(stac_item: stac_pb2.StacItem,
                   asset_type: stac_pb2.AssetType):
    for key in stac_item.assets:
        asset = stac_item.assets[key]
        if asset.asset_type == asset_type:
            return True
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
