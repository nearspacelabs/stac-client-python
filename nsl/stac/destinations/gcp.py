from pathlib import Path
from typing import Union

from google.cloud.storage import Blob, Bucket

from epl.protobuf.v1 import stac_pb2
from nsl.stac import gcs_storage_client
from nsl.stac.enum import AssetType
from nsl.stac.destinations.base import BaseDestination


class GCPDestination(BaseDestination):
    # TODO: GKE access to a bucket w/in the same region is Free
    # TODO: "transfer" between buckets w/in the same region is Free
    type = 'gcp'

    save_directory: Path
    bucket: str
    region: str

    def __init__(self,
                 bucket: str,
                 region: str,
                 asset_type: AssetType = AssetType.GEOTIFF,
                 save_directory: Union[Path, str] = '/'):
        super().__init__(asset_type=asset_type)
        self.save_directory = Path(save_directory)
        self.bucket = bucket
        self.region = region

    def deliver(self, nsl_id: str, sub_id: str, stac_item: stac_pb2.StacItem):
        try:
            # TODO: in the future, check a local cache for this asset to avoid multiple downloads
            self.target_blob(stac_item)\
                .upload_from_file(self.src_blob(stac_item).open('rb'), client=gcs_storage_client.client)
            return None
        except BaseException as err:
            print(f'ERROR: failed to transfer asset {stac_item.id}:\n{err}')
            raise err

    def __json__(self) -> dict:
        return dict(**super().__json__(),
                    bucket=self.bucket,
                    region=self.region,
                    save_directory=str(self.save_directory))

    def target_blob(self, stac_item: stac_pb2.StacItem) -> Blob:
        return Blob(name=self.blob_path(stac_item, self.save_directory),
                    bucket=Bucket(client=gcs_storage_client.client, name=self.bucket))
