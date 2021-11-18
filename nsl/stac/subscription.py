import json

from base64 import b64decode
from datetime import datetime, timezone

from epl.protobuf.v1 import stac_pb2

from nsl.stac.destinations import BaseDestination, DestinationDecoder
from nsl.stac.utils import stac_request_from_b64


class Subscription:
    id: str
    nsl_id: str
    is_active: bool
    created_at: datetime
    stac_request: stac_pb2.StacRequest
    destination: BaseDestination

    def __init__(self, response_dict: dict):
        self.id = response_dict['sub_id']
        self.nsl_id = response_dict['nsl_id']
        self.is_active = response_dict['is_active']
        self.created_at = datetime.utcfromtimestamp(response_dict['created_at']).replace(tzinfo=timezone.utc)
        self.stac_request = stac_request_from_b64(response_dict['stac_request'])
        self.destination = json.loads(response_dict['destination_json'], cls=DestinationDecoder)
