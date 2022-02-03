import json
from pathlib import Path
from typing import Iterator, Optional

from epl.protobuf.v1 import stac_pb2
from nsl.stac import Asset
from nsl.stac.enum import AssetType
from nsl.stac.utils import get_asset, get_blob_metadata


class BaseDestination(dict):
    type: str
    # TODO: make plural?
    asset_type: AssetType

    def __init__(self, asset_type: AssetType = AssetType.GEOTIFF):
        super().__init__(self)
        # FIXME: only allow co_geotiff, tiff and jpeg2000
        self.asset_type = asset_type

    @property
    def asset_type_str(self) -> str: return stac_pb2.AssetType.Name(self.asset_type)

    def deliver(self, nsl_id: str, sub_id: str, stac_item: stac_pb2.StacItem): pass

    def deliver_batch(self, nsl_id, sub_id: str, stac_items: Iterator[stac_pb2.StacItem]): pass

    def to_json_str(self) -> str: return json.dumps(self.__json__(), sort_keys=True)

    def __json__(self) -> dict: return dict(type=self.type, asset_type=self.asset_type_str)

    def file_name(self, stac_item: stac_pb2.StacItem) -> str:
        if self.asset_type == AssetType.TIFF or self.asset_type == AssetType.GEOTIFF:
            return f'{stac_item.id}.tif'
        elif self.asset_type == AssetType.THUMBNAIL:
            return Path(self.asset(stac_item).object_path).name
        elif self.asset_type == AssetType.JPEG:
            return f'{stac_item.id}.jpg'
        elif self.asset_type == AssetType.PNG:
            return f'{stac_item.id}.png'
        elif self.asset_type == AssetType.JPEG_2000:
            return f'{stac_item.id}.jp2'

        return stac_item.id

    def asset(self, stac_item: stac_pb2.StacItem) -> Optional[Asset]:
        return get_asset(stac_item=stac_item, asset_type=self.asset_type, b_relaxed_types=True)

    def src_blob(self, stac_item: stac_pb2.StacItem):
        asset = self.asset(stac_item)
        return get_blob_metadata(asset.bucket, asset.object_path)

    def blob_path(self, stac_item: stac_pb2.StacItem, root_dir=Path('/')) -> str:
        return str(root_dir.joinpath(self.file_name(stac_item)))


class DestinationDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct: dict) -> Optional[BaseDestination]:
        from nsl.stac.destinations.aws import AWSDestination
        from nsl.stac.destinations.gcp import GCPDestination
        from nsl.stac.destinations.memory import MemoryDestination

        destination_type = dct.get('type', '')
        asset_type = DestinationDecoder.asset_type_from_str(dct.get('asset_type', self.default_asset_type_str))

        dct = {k: dct[k] for k in dct if k not in {'type', 'asset_type'}}
        if destination_type == AWSDestination.type:
            return AWSDestination(asset_type=asset_type, **dct)
        if destination_type == GCPDestination.type:
            return GCPDestination(asset_type=asset_type, **dct)
        if destination_type == MemoryDestination.type:
            return MemoryDestination(asset_type=asset_type, **dct)
        return None

    @staticmethod
    def asset_type_from_str(s: str) -> AssetType: return AssetType(stac_pb2.AssetType.Value(s))

    @property
    def default_asset_type_str(self) -> str: return stac_pb2.AssetType.Name(stac_pb2.GEOTIFF)
