import os

# https://stackoverflow.com/a/16151611/445372
import datetime

from typing import Iterator

from google.protobuf import timestamp_pb2, duration_pb2
from epl.protobuf import stac_pb2

from st.stac import stac_service


def insert_one(stac_item: stac_pb2.StacItem) -> stac_pb2.StacDbResponse:
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    return stac_service.stub.InsertOne(stac_item, metadata=(
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


def timezoned(d_utc: datetime.datetime or datetime.date):
    # datetime is child to datetime.date, so if we reverse the order of this instance of we fail
    if isinstance(d_utc, datetime.datetime) and d_utc.tzinfo is None:
        # TODO add warning here:
        print("warning, no timezone provided with datetime, so UTC is assumed")
        d_utc = datetime.datetime(d_utc.year,
                                  d_utc.month,
                                  d_utc.day,
                                  d_utc.hour,
                                  d_utc.minute,
                                  d_utc.second,
                                  d_utc.microsecond,
                                  tzinfo=datetime.timezone.utc)
    elif not isinstance(d_utc, datetime.datetime):
        print("warning, no timezone provided with date, so UTC is assumed")
        d_utc = datetime.datetime.combine(d_utc, datetime.datetime.min.time(), tzinfo=datetime.timezone.utc)
    return d_utc


def timestamp(d_utc: datetime.datetime or datetime.date) -> timestamp_pb2.Timestamp:
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(timezoned(d_utc))
    return ts


def duration(d_start: datetime.date or datetime.datetime, d_end: datetime.date or datetime.datetime):
    d = duration_pb2.Duration()
    d.FromTimedelta(timezoned(d_end) - timezoned(d_start))
    return d
