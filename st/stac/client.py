import os

from datetime import datetime, timezone, date
from typing import Iterator

from google.protobuf import timestamp_pb2, duration_pb2
from epl.protobuf import stac_pb2

from st.stac import stac_service


def insert_one(self, stac_item: stac_pb2.StacItem) -> stac_pb2.StacDbResponse:
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    return self.stac_stub.InsertOne(stac_item, metadata=(
        ('authorization', auth),
        ('bearer', bearer),
    ))


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


def utc_datetime(d_utc: datetime or date):
    if isinstance(d_utc, date):
        d_utc = datetime.combine(d_utc, datetime.min.time(), tzinfo=timezone.utc)
    else:
        d_utc = d_utc.astimezone(tz=timezone.utc)
    return d_utc


def timestamp(d_utc: datetime or date) -> timestamp_pb2.Timestamp:
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(utc_datetime(d_utc))
    return ts


def duration(d_start: date or datetime, d_end: date or datetime):
    d = duration_pb2.Duration()
    d.FromTimedelta(utc_datetime(d_end) - utc_datetime(d_start))
    return d
