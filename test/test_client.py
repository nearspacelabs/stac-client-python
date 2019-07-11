import unittest

from datetime import datetime, timezone, date

from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf import query_pb2

from st.stac.client import timestamp, search_one, search


class TestDatetimeQueries(unittest.TestCase):
    def test_date_GT_OR_EQ(self):
        bd = date(2015, 11, 3)
        observed_range = query_pb2.TimestampField(value=timestamp(bd),
                                                  rel_type=query_pb2.GT_OR_EQ)
        stac_request = StacRequest(observed=observed_range)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(timestamp(bd).seconds, stac_item.datetime.seconds)

    def test_datetime_GT(self):
        bdt = datetime(2015, 11, 3, 1, 1, 1, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(value=timestamp(bdt),
                                                  rel_type=query_pb2.GT)
        stac_request = StacRequest(observed=observed_range)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(timestamp(bdt).seconds, stac_item.datetime.seconds)

    def test_datetime_range(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(between_value1=timestamp(start),
                                                  between_value2=timestamp(end),
                                                  rel_type=query_pb2.BETWEEN)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertGreaterEqual(timestamp(end).seconds, stac_item.datetime.seconds)
            self.assertLessEqual(timestamp(start).seconds, stac_item.datetime.seconds)

    def test_datetime_not_range(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(between_value1=timestamp(start),
                                                  between_value2=timestamp(end),
                                                  rel_type=query_pb2.NOT_BETWEEN)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(timestamp(end).seconds < stac_item.datetime.seconds or
                            timestamp(start).seconds > stac_item.datetime.seconds)

    def test_datetime_not_range_asc(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(between_value1=timestamp(start),
                                                  between_value2=timestamp(end),
                                                  rel_type=query_pb2.NOT_BETWEEN,
                                                  sort_direction=query_pb2.ASC)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(timestamp(start).seconds > stac_item.datetime.seconds)

    def test_datetime_not_range_desc(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(between_value1=timestamp(start),
                                                  between_value2=timestamp(end),
                                                  rel_type=query_pb2.NOT_BETWEEN,
                                                  sort_direction=query_pb2.DESC)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(timestamp(end).seconds < stac_item.datetime.seconds)
