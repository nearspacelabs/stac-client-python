from pathlib import Path
from typing import Union

from epl.protobuf.v1 import stac_pb2
from nsl.stac.destinations.base import BaseDestination
from nsl.stac.enum import AssetType
from nsl.stac.utils import download_asset


class MemoryDestination(BaseDestination):
    type = 'memory'
    save_directory: Path

    def __init__(self, asset_type: AssetType = AssetType.GEOTIFF, save_directory: Union[Path, str] = '/'):
        super().__init__(asset_type=asset_type)
        self.save_directory = Path(save_directory)

    def deliver(self, nsl_id: str, sub_id: str, stac_item: stac_pb2.StacItem):
        try:
            file_path = self.save_directory.joinpath(self.file_name(stac_item))
            download_asset(asset=self.asset(stac_item),
                           from_bucket=True,
                           save_filename=str(file_path))
            return None
        except BaseException as err:
            print(f'ERROR: failed downloading asset for {stac_item.id}:\n{err}')
            raise err

    def __json__(self) -> dict:
        return dict(**super().__json__(), save_directory=str(self.save_directory))
