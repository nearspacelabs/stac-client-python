import os

from pathlib import Path
from typing import Optional, Union

import boto3

from epl.protobuf.v1 import stac_pb2
from nsl.stac.enum import AssetType
from nsl.stac.destinations.base import BaseDestination

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


class AWSDestination(BaseDestination):
    type = 'aws'

    _client = None
    save_directory: Path
    role_arn: str
    bucket: str
    region: str

    def __init__(self,
                 role_arn: str,
                 bucket: str,
                 region: str,
                 asset_type: AssetType = AssetType.GEOTIFF,
                 save_directory: Union[Path, str] = '/'):
        super().__init__(asset_type=asset_type)
        self.save_directory = Path(save_directory)
        self.role_arn = role_arn
        self.bucket = bucket
        self.region = region

    def deliver(self, nsl_id: str, sub_id: str, stac_item: stac_pb2.StacItem):
        try:
            # TODO: in the future, check a local cache for this asset to avoid multiple downloads
            self.target_obj(stac_item).upload_fileobj(self.src_blob(stac_item).open('rb'))
            return None
        except BaseException as err:
            print(f'ERROR: failed to transfer asset {stac_item.id}:\n{err}')
            raise err

    def __json__(self) -> dict:
        return dict(**super().__json__(),
                    role_arn=self.role_arn,
                    bucket=self.bucket,
                    region=self.region,
                    save_directory=str(self.save_directory))

    def target_obj(self, stac_item: stac_pb2.StacItem) -> Optional[object]:
        return self.s3.Object(self.bucket, self.blob_path(stac_item, self.save_directory))

    @property
    def s3(self):
        if self._client is None:
            client = boto3\
                .Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)\
                .client('sts')
            assumed_role = client.assume_role(RoleArn=self.role_arn, RoleSessionName='nearspacelabs')
            credentials = assumed_role['Credentials']
            self._client = boto3.resource('s3',
                                          aws_access_key_id=credentials['AccessKeyId'],
                                          aws_secret_access_key=credentials['SecretAccessKey'],
                                          aws_session_token=credentials['SessionToken'])
        return self._client
