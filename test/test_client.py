import tempfile
import unittest

from google.protobuf import timestamp_pb2
from datetime import datetime, timezone, date, timedelta

from epl.protobuf.stac_pb2 import StacRequest, StacItem, LandsatRequest, AWS, GCP, Eo, Asset, THUMBNAIL, TXT
from epl.protobuf import query_pb2

from nsl.stac.client import NSLClient
from nsl.stac import utils

client = NSLClient()


class TestProtobufs(unittest.TestCase):
    def test_durations(self):
        d = utils.duration(datetime(2016, 1, 1), datetime(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)
        d = utils.duration(date(2016, 1, 1), datetime(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)
        d = utils.duration(date(2016, 1, 1), date(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)
        d = utils.duration(datetime(2016, 1, 1), date(2017, 1, 1))
        self.assertEquals(d.seconds, 31622400)

        td = timedelta(seconds=d.seconds)
        d_end = datetime(2016, 1, 1) + td
        self.assertEquals(d_end.year, 2017)
        self.assertEquals(d_end.day, 1)
        self.assertEquals(d_end.month, 1)

        # FromDatetime for protobuf 3.6.1 throws "TypeError: can't subtract offset-naive and offset-aware datetimes"
        ts = utils.pb_timestamp(datetime(2016, 1, 1, tzinfo=timezone.utc))
        self.assertIsNotNone(ts)

        d = utils.duration(datetime(2017, 1, 1), datetime(2017, 1, 1, 0, 0, 59))
        self.assertEquals(d.seconds, 59)

        now_local = datetime.now().astimezone()
        now_utc = datetime.now(tz=timezone.utc)
        d = utils.duration(now_local, now_utc)
        self.assertLess(d.seconds, 1)

        ts = utils.pb_timestamp(now_local)
        ts2 = timestamp_pb2.Timestamp()
        ts2.FromDatetime(now_local)
        self.assertEquals(ts.seconds, ts2.seconds)

        d = utils.duration(datetime(2016, 1, 1, 0, 0, 59, tzinfo=timezone.utc),
                           datetime(2016, 1, 1, 0, 1, 59, tzinfo=timezone.utc))
        self.assertEquals(d.seconds, 60)

        utc_now = now_local.astimezone(tz=timezone.utc)
        later_now = utc_now + timedelta(seconds=33)

        d = utils.duration(now_local, later_now)
        self.assertEquals(d.seconds, 33)


class TestAssetMatching(unittest.TestCase):
    def test_asset_match(self):
        asset_1 = Asset(href="pecans")
        asset_2 = Asset(href="walnuts")
        stac_item = StacItem()
        stac_item.assets["test_key"].CopyFrom(asset_1)
        self.assertFalse(utils.has_asset(stac_item, asset_2))


class TestLandsat(unittest.TestCase):
    def test_product_id(self):
        product_id = "LC08_L1TP_027039_20150226_20170228_01_T1"
        stac_request = StacRequest(landsat=LandsatRequest(product_id=product_id))
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertEquals("LC80270392015057LGN01", stac_item.id)

    def test_wrs_row_path(self):
        wrs_path = 27
        wrs_row = 38

        stac_request = StacRequest(landsat=LandsatRequest(wrs_path=wrs_path, wrs_row=wrs_row))
        stac_item = client.search_one(stac_request)
        self.assertNotEqual(len(stac_item.id), 0)

    def test_OLI(self):
        stac_id = "LO81120152015061LGN00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
        asset = utils.get_asset(stac_item, band=Eo.BLUE, cloud_platform=GCP)
        self.assertIsNotNone(asset)
        asset = utils.get_asset(stac_item, band=Eo.BLUE, cloud_platform=AWS)
        self.assertIsNotNone(asset)

        asset = utils.get_asset(stac_item, band=Eo.LWIR_1, cloud_platform=GCP)
        self.assertIsNone(asset)
        asset = utils.get_asset(stac_item, band=Eo.LWIR_1, cloud_platform=AWS)
        self.assertIsNone(asset)

        asset = utils.get_asset(stac_item, band=Eo.CIRRUS, cloud_platform=GCP)
        self.assertIsNotNone(asset)
        asset = utils.get_asset(stac_item, band=Eo.CIRRUS, cloud_platform=AWS)
        self.assertIsNotNone(asset)

        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                print(asset.object_path)
                aws_count += 1
            else:
                # print(asset.object_path)
                gcp_count += 1
        self.assertEquals(25, aws_count)
        self.assertEquals(12, gcp_count)

    def test_basename(self):
        asset_name = 'LO81120152015061LGN00_B2.TIF'
        stac_id = "LO81120152015061LGN00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
        asset = utils.get_asset(stac_item, asset_basename=asset_name)
        self.assertIsNotNone(asset)

    def test_thumbnail(self):
        stac_id = 'LO81120152015061LGN00'
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
        asset_type = THUMBNAIL
        asset = utils.get_asset(stac_item, asset_types=[asset_type], cloud_platform=AWS)
        self.assertIsNotNone(asset)

    def test_aws(self):
        stac_id = "LC80270392015025LGN00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        count = 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                print(asset.object_path)
                count += 1
        self.assertEquals(29, count)

    def test_L1TP(self):
        stac_id = "LT51560171989121KIS00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
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
        stac_id = "LT51560202010035IKR02"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
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
        stac_id = "LT50590132011238PAC00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
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
        stac_id = "LE70080622016239EDC00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
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
        stac_id = "LC81262052018263LGN00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                aws_count += 1
            else:
                print(asset.object_path)
                gcp_count += 1
        self.assertEquals(42, aws_count)
        self.assertEquals(14, gcp_count)

    def test_L8_processed_id_2(self):
        stac_id = "LC81262052018263LGN00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == AWS:
                aws_count += 1
                print(asset.object_path)
            else:
                gcp_count += 1
        self.assertEquals(42, aws_count)
        self.assertEquals(14, gcp_count)

    def test_count(self):
        stac_id = "LC81262052018263LGN00"
        stac_request = StacRequest(id=stac_id)
        number = client.count(stac_request)
        self.assertEquals(1, number)

    def test_count_more(self):
        start = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 52, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(start=utils.pb_timestamp(start),
                                                  stop=utils.pb_timestamp(end),
                                                  rel_type=query_pb2.BETWEEN)
        stac_request = StacRequest(observed=observed_range, limit=40, landsat=LandsatRequest())
        for stac_item in client.search(stac_request):
            self.assertEquals(Eo.LANDSAT, stac_item.eo.constellation)
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertGreaterEqual(utils.pb_timestamp(end).seconds, stac_item.datetime.seconds)
            self.assertLessEqual(utils.pb_timestamp(start).seconds, stac_item.datetime.seconds)

        self.assertEquals(12, client.count(stac_request))


class TestDatetimeQueries(unittest.TestCase):
    def test_date_GT_OR_EQ(self):
        bd = date(2015, 11, 3)
        observed_range = query_pb2.TimestampField(value=utils.pb_timestamp(bd),
                                                  rel_type=query_pb2.GT_OR_EQ)
        stac_request = StacRequest(observed=observed_range)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(utils.pb_timestamp(bd).seconds, stac_item.datetime.seconds)

    def test_datetime_GT(self):
        bdt = datetime(2015, 11, 3, 1, 1, 1, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(value=utils.pb_timestamp(bdt),
                                                  rel_type=query_pb2.GT)
        stac_request = StacRequest(observed=observed_range)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(utils.pb_timestamp(bdt).seconds, stac_item.datetime.seconds)

    def test_datetime_range(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(start=utils.pb_timestamp(start),
                                                  stop=utils.pb_timestamp(end),
                                                  rel_type=query_pb2.BETWEEN)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in client.search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertGreaterEqual(utils.pb_timestamp(end).seconds, stac_item.datetime.seconds)
            self.assertLessEqual(utils.pb_timestamp(start).seconds, stac_item.datetime.seconds)

    def test_datetime_not_range(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(start=utils.pb_timestamp(start),
                                                  stop=utils.pb_timestamp(end),
                                                  rel_type=query_pb2.NOT_BETWEEN)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in client.search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(utils.pb_timestamp(end).seconds < stac_item.datetime.seconds or
                            utils.pb_timestamp(start).seconds > stac_item.datetime.seconds)

    def test_datetime_not_range_asc(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(start=utils.pb_timestamp(start),
                                                  stop=utils.pb_timestamp(end),
                                                  rel_type=query_pb2.NOT_BETWEEN,
                                                  sort_direction=query_pb2.ASC)
        stac_request = StacRequest(observed=observed_range, limit=5)
        count = 0
        for stac_item in client.search(stac_request):
            count += 1
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(utils.pb_timestamp(end).seconds > stac_item.datetime.seconds or
                            utils.pb_timestamp(start).seconds < stac_item.datetime.seconds)
        self.assertEqual(count, 5)

    def test_datetime_not_range_desc(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = query_pb2.TimestampField(start=utils.pb_timestamp(start),
                                                  stop=utils.pb_timestamp(end),
                                                  rel_type=query_pb2.NOT_BETWEEN,
                                                  sort_direction=query_pb2.DESC)
        stac_request = StacRequest(observed=observed_range, limit=5)
        count = 0
        for stac_item in client.search(stac_request):
            count += 1
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(utils.pb_timestamp(end).seconds < stac_item.datetime.seconds)
        self.assertEqual(count, 5)


class TestHelpers(unittest.TestCase):
    def test_has_asset(self):
        stac_id = "LO81120152015061LGN00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request=stac_request)
        for key in stac_item.assets:
            asset = stac_item.assets[key]
            self.assertTrue(utils.has_asset(stac_item, asset))
            garbage = Asset(href="pie")
            self.assertFalse(utils.has_asset(stac_item, garbage))
            garbage.asset_type = asset.asset_type
            self.assertFalse(utils.has_asset(stac_item, garbage))
            garbage.href = asset.href
            garbage.bucket = asset.bucket
            garbage.type = asset.type
            garbage.eo_bands = asset.eo_bands
            garbage.cloud_platform = asset.cloud_platform
            garbage.bucket_manager = asset.bucket_manager
            garbage.bucket_region = asset.bucket_region
            garbage.object_path = asset.object_path
            self.assertTrue(utils.has_asset(stac_item, garbage))

    def test_download_gcp(self):
        stac_id = "LO81120152015061LGN00"
        stac_item = client.search_one(stac_request=StacRequest(id=stac_id))
        asset = utils.get_asset(stac_item,
                                asset_types=[TXT],
                                cloud_platform=GCP,
                                asset_basename='LO81120152015061LGN00_MTL.txt')
        self.assertIsNotNone(asset)
        with tempfile.TemporaryDirectory() as d:
            print(d)
            file_path = utils.download_asset(asset=asset, from_bucket=True, save_directory=d)
            with open(file_path) as f:
                data1 = f.read()

            file_path = utils.download_asset(asset=asset, from_bucket=True, save_filename=file_path)
            with open(file_path) as f:
                data2 = f.read()

            self.assertMultiLineEqual(data1, data2)

            with tempfile.NamedTemporaryFile('w+b', delete=False) as f_obj:
                utils.download_asset(asset=asset, from_bucket=True, file_obj=f_obj)
                data3 = f_obj.read().decode('ascii')
                self.assertMultiLineEqual(data1, data3)

    def test_download_aws(self):
        stac_id = "LC80270392015025LGN00"
        stac_item = client.search_one(stac_request=StacRequest(id=stac_id))
        asset = utils.get_asset(stac_item,
                                asset_types=[TXT],
                                cloud_platform=AWS)
        self.assertIsNotNone(asset)
        with tempfile.TemporaryDirectory() as d:
            print(d)
            file_path = utils.download_asset(asset=asset, from_bucket=True, save_directory=d)
            with open(file_path) as f:
                data1 = f.read()

            file_path = utils.download_asset(asset=asset, from_bucket=True, save_filename=file_path)
            with open(file_path) as f:
                data2 = f.read()

            self.assertMultiLineEqual(data1, data2)

            with tempfile.NamedTemporaryFile('w+b', delete=False) as f_obj:
                utils.download_asset(asset=asset, from_bucket=True, file_obj=f_obj)
                data3 = f_obj.read().decode('ascii')
                self.assertMultiLineEqual(data1, data3)

    def test_download_href(self):
        stac_id = "20191121T192629Z_1594_ST2_POM1"
        stac_item = client.search_one(stac_request=StacRequest(id=stac_id))
        asset = utils.get_asset(stac_item, asset_types=[THUMBNAIL])

        self.assertIsNotNone(asset)

        with tempfile.TemporaryDirectory() as d:
            file_path = utils.download_asset(asset=asset, save_directory=d)
            with open(file_path, 'rb') as f:
                data1 = f.read()

            file_path = utils.download_asset(asset=asset, save_filename=file_path)
            with open(file_path, 'rb') as f:
                data2 = f.read()

            self.assertEqual(data1, data2)

            with tempfile.NamedTemporaryFile('w+b', delete=False) as file_obj:
                utils.download_asset(asset=asset, file_obj=file_obj)
                data3 = file_obj.read()
                self.assertEqual(data1, data3)
