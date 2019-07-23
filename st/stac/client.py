import os

from datetime import datetime, timezone, date
from typing import Iterator

from google.protobuf import timestamp_pb2
from epl.protobuf import stac_pb2

from st.stac import stac_service


def search_one(stac_request: stac_pb2.StacRequest) -> stac_pb2.StacItem:
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    return stac_service.stub.SearchOne(stac_request, metadata=(
        ('authorization', auth),
        ('bearer', bearer),
    ))


def search(stac_request: stac_pb2.StacRequest) -> Iterator[stac_pb2.StacItem]:
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    results_generator = stac_service.stub.Search(stac_request, metadata=(
        ('authorization', auth),
        ('bearer', bearer),
    ))
    return results_generator


def timestamp(d_utc: datetime or date) -> timestamp_pb2.Timestamp:
    if isinstance(d_utc, datetime):
        ts = timestamp_pb2.Timestamp()
        ts.seconds = int(d_utc.astimezone(tz=timezone.utc).timestamp())
        return ts
    elif isinstance(d_utc, date):
        d_utc = datetime.combine(d_utc, datetime.min.time(), tzinfo=timezone.utc)
        return timestamp(d_utc)
