import unittest

from google.protobuf import timestamp_pb2
from datetime import datetime, timezone, date, timedelta

from epl.protobuf.stac_pb2 import StacRequest, LandsatRequest, AWS, GCP, Eo, Asset
from epl.protobuf import query_pb2

from st.stac.client import timestamp, search_one, search, duration
from st.stac import raster


class TestProtobufs(unittest.TestCase):
    def test_durations(self):
        d = duration(datetime(2016, 1, 1), datetime(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)
        d = duration(date(2016, 1, 1), datetime(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)
        d = duration(date(2016, 1, 1), date(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)
        d = duration(datetime(2016, 1, 1), date(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)

        td = timedelta(seconds=d.seconds)
        d_end = datetime(2016, 1, 1) + td
        self.assertEquals(d_end.year, 2017)
        self.assertEquals(d_end.day, 1)
        self.assertEquals(d_end.month, 1)

        # FromDatetime for protobuf 3.6.1 throws "TypeError: can't subtract offset-naive and offset-aware datetimes"
        ts = timestamp(datetime(2016, 1, 1, tzinfo=timezone.utc))
        self.assertIsNotNone(ts)

        d = duration(datetime(2017, 1, 1), datetime(2017, 1, 1, 0, 0, 59))
        self.assertEquals(d.seconds, 59)

        now_local = datetime.now().astimezone()
        now_utc = datetime.now(tz=timezone.utc)
        d = duration(now_local, now_utc)
        self.assertLess(d.seconds, 1)

        ts = timestamp(now_local)
        ts2 = timestamp_pb2.Timestamp()
        ts2.FromDatetime(now_local)
        self.assertEquals(ts.seconds, ts2.seconds)

        d = duration(datetime(2016, 1, 1, 0, 0, 59, tzinfo=timezone.utc),
                     datetime(2016, 1, 1, 0, 1, 59, tzinfo=timezone.utc))
        self.assertEquals(d.seconds, 60)

        utc_now = now_local.astimezone(tz=timezone.utc)
        later_now = utc_now + timedelta(seconds=33)

        d = duration(now_local, later_now)
        self.assertEquals(d.seconds, 33)


class TestLandsat(unittest.TestCase):
    def test_product_id(self):
        product_id = "LC08_L1TP_027039_20150226_20170228_01_T1"
        stac_request = StacRequest(landsat=LandsatRequest(product_id=product_id))
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertEquals("LC80270392015057LGN01", stac_item.id)

    def test_wrs_row_path(self):
        wrs_path = 27
        wrs_row = 38

        stac_request = StacRequest(landsat=LandsatRequest(wrs_path=wrs_path, wrs_row=wrs_row))
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)

    def test_OLI(self):
        id = "LO81120152015061LGN00"
        stac_request = StacRequest(id=id)
        stac_item = search_one(stac_request)
        asset = raster.get_asset(stac_item, band=Eo.BLUE, cloud_platform=GCP)
        self.assertIsNotNone(asset)
        asset = raster.get_asset(stac_item, band=Eo.BLUE, cloud_platform=AWS)
        self.assertIsNotNone(asset)

        asset = raster.get_asset(stac_item, band=Eo.LWIR_1, cloud_platform=GCP)
        self.assertIsNone(asset)
        asset = raster.get_asset(stac_item, band=Eo.LWIR_1, cloud_platform=AWS)
        self.assertIsNone(asset)

        asset = raster.get_asset(stac_item, band=Eo.CIRRUS, cloud_platform=GCP)
        self.assertIsNotNone(asset)
        asset = raster.get_asset(stac_item, band=Eo.CIRRUS, cloud_platform=AWS)
        self.assertIsNotNone(asset)

        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                print(asset.object_path)
                aws_count += 1
            else:
                # print(asset.object_path)
                gcp_count += 1
        self.assertEquals(36, aws_count)
        self.assertEquals(12, gcp_count)

    def test_aws(self):
        id="LC80270392015025LGN00"
        stac_request = StacRequest(id=id)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        count = 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                print(asset.object_path)
                count += 1
        self.assertEquals(42, count)

    def test_L1TP(self):
        id="LT51560171989121KIS00"
        stac_request = StacRequest(id = id)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                aws_count += 1
            else:
                print(asset.object_path)
                gcp_count += 1
        self.assertEquals(0, aws_count)
        self.assertEquals(20, gcp_count)

    def test_L1G(self):
        id="LT51560202010035IKR02"
        stac_request = StacRequest(id = id)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                aws_count += 1
            else:
                print(asset.object_path)
                gcp_count += 1
        self.assertEquals(0, aws_count)
        self.assertEquals(20, gcp_count)

    def test_L1t(self):
        id="LT50590132011238PAC00"
        stac_request = StacRequest(id = id)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                aws_count += 1
            else:
                print(asset.object_path)
                gcp_count += 1
        self.assertEquals(0, aws_count)
        self.assertEquals(20, gcp_count)

    def test_L1GT(self):
        id="LE70080622016239EDC00"
        stac_request = StacRequest(id = id)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                aws_count += 1
            else:
                print(asset.object_path)
                gcp_count += 1
        self.assertEquals(0, aws_count)
        self.assertEquals(22, gcp_count)

    def test_L8_processed_id(self):
        id = "LC81262052018263LGN00"
        stac_request = StacRequest(id = id)
        stac_item = search_one(stac_request)
        self.assertIsNotNone(stac_item)
        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                aws_count += 1
            else:
                print(asset.object_path)
                gcp_count += 1
        self.assertEquals(56, aws_count)
        self.assertEquals(14, gcp_count)


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


class TestHelpers(unittest.TestCase):
    def test_has_asset(self):
        id = "LO81120152015061LGN00"
        stac_request = StacRequest(id=id)
        stac_item = search_one(stac_request=stac_request)
        for key in stac_item.assets:
            asset = stac_item.assets[key]
            self.assertTrue(raster.has_asset(stac_item, asset))
            garbage = Asset(href="pie")
            self.assertFalse(raster.has_asset(stac_item, garbage))
            garbage.asset_type = asset.asset_type
            self.assertFalse(raster.has_asset(stac_item, garbage))
            garbage.href = asset.href
            self.assertTrue(raster.has_asset(stac_item, garbage))
