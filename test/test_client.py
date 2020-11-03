# Copyright 2019-20 Near Space Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# for additional information, contact:
#   info@nearspacelabs.com

import tempfile
import unittest
import io
import os

from google.protobuf import timestamp_pb2
from datetime import datetime, timezone, date, timedelta

from nsl.stac import StacRequest, LandsatRequest, MosaicRequest
from nsl.stac import StacItem, Asset, TimestampFilter, GeometryData, ProjectionData, Mosaic
from nsl.stac import utils, enum
from nsl.stac.enum import AssetType, Band, CloudPlatform, Mission, FilterRelationship
from nsl.stac.client import NSLClient

client = NSLClient(nsl_only=False)


class TestProtobufs(unittest.TestCase):
    def test_mosaic_parts(self):
        mosaic = Mosaic(name="bananas", quad_key="stuff", provenance_ids=["no one", "wants", "potato", "waffles"])

        self.assertEqual(mosaic.name, "bananas")
        mosaic.observation_range.CopyFrom(utils.datetime_range(date(2016, 1, 1), date(2018, 1, 1)))
        d_compare = utils.timezoned(date(2019, 1, 1))
        self.assertGreater(d_compare.timestamp(), mosaic.observation_range.start.seconds)
        self.assertGreater(d_compare.timestamp(), mosaic.observation_range.end.seconds)

        self.assertEqual(mosaic.provenance_ids[0], "no one")
        self.assertEqual(4, len(mosaic.provenance_ids))
        mosaic.provenance_ids.append("and boiled chicken")
        self.assertEqual(5, len(mosaic.provenance_ids))
        mosaic_request = MosaicRequest(name="bananas", quad_key="stuffly")
        self.assertEqual(mosaic_request.name, mosaic.name)
        stac_item = StacItem(mosaic=mosaic)
        self.assertEqual(stac_item.mosaic.name, mosaic.name)

        stac_request = StacRequest(mosaic=mosaic_request)
        self.assertEqual(stac_request.mosaic.name, mosaic.name)

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
        asset = utils.get_asset(stac_item, band=Band.BLUE, cloud_platform=CloudPlatform.GCP)
        self.assertIsNotNone(asset)
        asset = utils.get_asset(stac_item, band=Band.BLUE, cloud_platform=CloudPlatform.AWS)
        self.assertIsNotNone(asset)

        asset = utils.get_asset(stac_item, band=Band.LWIR_1, cloud_platform=CloudPlatform.GCP)
        self.assertIsNone(asset)
        asset = utils.get_asset(stac_item, band=Band.LWIR_1, cloud_platform=CloudPlatform.AWS)
        self.assertIsNone(asset)

        asset = utils.get_asset(stac_item, band=Band.CIRRUS, cloud_platform=CloudPlatform.GCP)
        self.assertIsNotNone(asset)
        asset = utils.get_asset(stac_item, band=Band.CIRRUS, cloud_platform=CloudPlatform.AWS)
        self.assertIsNotNone(asset)

        aws_count, gcp_count = 0, 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == CloudPlatform.AWS:
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
        asset = utils.get_asset(stac_item, asset_type=AssetType.THUMBNAIL, cloud_platform=CloudPlatform.AWS)
        self.assertIsNotNone(asset)

    def test_aws(self):
        stac_id = "LC80270392015025LGN00"
        stac_request = StacRequest(id=stac_id)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        count = 0
        for key, asset in stac_item.assets.items():
            if asset.cloud_platform == CloudPlatform.AWS:
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
            if asset.cloud_platform == CloudPlatform.AWS:
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
            if asset.cloud_platform == CloudPlatform.AWS:
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
            if asset.cloud_platform == CloudPlatform.AWS:
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
            if asset.cloud_platform == CloudPlatform.AWS:
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
            if asset.cloud_platform == CloudPlatform.AWS:
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
            if asset.cloud_platform == CloudPlatform.AWS:
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

    def test_2000(self):
        start = datetime(1999, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(1999, 4, 6, 12, 52, 59, tzinfo=timezone.utc)
        observed_range = utils.pb_timestampfield(rel_type=FilterRelationship.BETWEEN, start=start, end=end)

        stac_request = StacRequest(observed=observed_range, limit=20, landsat=LandsatRequest())
        for stac_item in client.search(stac_request):
            self.assertEqual(Mission.LANDSAT, stac_item.mission_enum)
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertGreaterEqual(utils.pb_timestamp(end).seconds, stac_item.datetime.seconds)
            self.assertLessEqual(utils.pb_timestamp(start).seconds, stac_item.datetime.seconds)

        self.assertEquals(2728, client.count(stac_request))

    def test_count_more(self):
        start = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 52, 59, tzinfo=timezone.utc)
        observed_range = TimestampFilter(start=utils.pb_timestamp(start),
                                         end=utils.pb_timestamp(end),
                                         rel_type=FilterRelationship.BETWEEN)

        stac_request = StacRequest(observed=observed_range, limit=40, landsat=LandsatRequest())
        for stac_item in client.search(stac_request):
            self.assertEquals(Mission.LANDSAT, stac_item.mission_enum)
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertGreaterEqual(utils.pb_timestamp(end).seconds, stac_item.datetime.seconds)
            self.assertLessEqual(utils.pb_timestamp(start).seconds, stac_item.datetime.seconds)

        self.assertEquals(12, client.count(stac_request))


class TestDatetimeQueries(unittest.TestCase):
    def test_date_LT_OR_EQ(self):
        bd = date(2014, 11, 3)
        observed_range = utils.pb_timestampfield(rel_type=FilterRelationship.LTE, value=bd)
        stac_request = StacRequest(observed=observed_range, mission_enum=enum.Mission.NAIP)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(utils.pb_timestamp(bd).seconds, stac_item.datetime.seconds)

    def test_date_GT_OR_EQ(self):
        bd = date(2015, 11, 3)
        observed_range = TimestampFilter(value=utils.pb_timestamp(bd, tzinfo=timezone.utc),
                                         rel_type=FilterRelationship.GTE)
        stac_request = StacRequest(observed=observed_range)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(utils.pb_timestamp(bd, tzinfo=timezone.utc).seconds, stac_item.observed.seconds)

    def test_date_GT_OR_EQ_datetime(self):
        bd = date(2015, 11, 3)
        observed_range = TimestampFilter(value=utils.pb_timestamp(bd, tzinfo=timezone.utc),
                                         rel_type=FilterRelationship.GTE)
        stac_request = StacRequest(observed=observed_range)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(utils.pb_timestamp(bd, tzinfo=timezone.utc).seconds, stac_item.datetime.seconds)

    def test_observed_GT(self):
        bdt = datetime(2015, 11, 3, 1, 1, 1, tzinfo=timezone.utc)
        observed_range = TimestampFilter(value=utils.pb_timestamp(bdt),
                                         rel_type=FilterRelationship.GT)
        stac_request = StacRequest(observed=observed_range)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(utils.pb_timestamp(bdt).seconds, stac_item.observed.seconds)

    def test_datetime_GT(self):
        bdt = datetime(2015, 11, 3, 1, 1, 1, tzinfo=timezone.utc)
        observed_range = TimestampFilter(value=utils.pb_timestamp(bdt),
                                         rel_type=FilterRelationship.GT)
        stac_request = StacRequest(observed=observed_range)
        stac_item = client.search_one(stac_request)
        self.assertIsNotNone(stac_item)
        self.assertLessEqual(utils.pb_timestamp(bdt).seconds, stac_item.datetime.seconds)

    def test_datetime_range(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = TimestampFilter(start=utils.pb_timestamp(start),
                                         end=utils.pb_timestamp(end),
                                         rel_type=FilterRelationship.BETWEEN)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in client.search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertGreaterEqual(utils.pb_timestamp(end).seconds, stac_item.datetime.seconds)
            self.assertLessEqual(utils.pb_timestamp(start).seconds, stac_item.datetime.seconds)

    def test_datetime_not_range(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = TimestampFilter(start=utils.pb_timestamp(start),
                                         end=utils.pb_timestamp(end),
                                         rel_type=FilterRelationship.NOT_BETWEEN)
        stac_request = StacRequest(observed=observed_range, limit=5)
        for stac_item in client.search(stac_request):
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(utils.pb_timestamp(end).seconds < stac_item.datetime.seconds or
                            utils.pb_timestamp(start).seconds > stac_item.datetime.seconds)

    def test_datetime_not_range_asc(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = TimestampFilter(start=utils.pb_timestamp(start),
                                         end=utils.pb_timestamp(end),
                                         rel_type=FilterRelationship.NOT_BETWEEN,
                                         sort_direction=enum.SortDirection.ASC)
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
        observed_range = TimestampFilter(start=utils.pb_timestamp(start),
                                         end=utils.pb_timestamp(end),
                                         rel_type=FilterRelationship.NOT_BETWEEN,
                                         sort_direction=enum.SortDirection.DESC)
        stac_request = StacRequest(observed=observed_range, limit=5)
        count = 0
        for stac_item in client.search(stac_request):
            count += 1
            print(datetime.fromtimestamp(stac_item.datetime.seconds, tz=timezone.utc))
            self.assertTrue(utils.pb_timestamp(end).seconds < stac_item.datetime.seconds)
        self.assertEqual(count, 5)

    def test_observed_not_range_desc(self):
        start = datetime(2013, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        end = datetime(2014, 4, 1, 12, 45, 59, tzinfo=timezone.utc)
        observed_range = TimestampFilter(start=utils.pb_timestamp(start),
                                         end=utils.pb_timestamp(end),
                                         rel_type=FilterRelationship.NOT_BETWEEN,
                                         sort_direction=enum.SortDirection.DESC)
        stac_request = StacRequest(observed=observed_range, limit=5)
        count = 0
        for stac_item in client.search(stac_request):
            count += 1
            print(datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc))
            self.assertTrue(utils.pb_timestamp(end).seconds < stac_item.observed.seconds)
        self.assertEqual(count, 5)

    def test_date_utc_eq(self):
        value = date(2019, 8, 6)
        texas_utc_offset = timezone(timedelta(hours=-6))
        time_filter = utils.pb_timestampfield(rel_type=enum.FilterRelationship.EQ,
                                              value=value,
                                              tzinfo=texas_utc_offset)

        stac_request = StacRequest(datetime=time_filter, limit=2)

        # get a client interface to the gRPC channel
        for stac_item in client.search(stac_request):
            print("STAC item date, {0}, is before {1}: {2}".format(
                datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
                datetime.fromtimestamp(time_filter.end.seconds, tz=texas_utc_offset).isoformat(),
                stac_item.observed.seconds < time_filter.end.seconds))

        start = date(2019, 8, 6)
        time_filter = utils.pb_timestampfield(rel_type=FilterRelationship.EQ,
                                              value=start,
                                              tzinfo=timezone(timedelta(hours=-6)))
        stac_request = StacRequest(datetime=time_filter, limit=2)
        count = 0
        for _ in client.search(stac_request):
            count += 1

        self.assertEqual(2, count)


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
                                asset_type=AssetType.TXT,
                                cloud_platform=CloudPlatform.GCP,
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
                                asset_type=AssetType.TXT,
                                cloud_platform=CloudPlatform.AWS)
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

    def test_download_geotiff(self):
        stac_request = StacRequest(id='20190822T183518Z_746_POM1_ST2_P')

        stac_item = client.search_one(stac_request)

        # get the Geotiff asset from the assets map
        asset = utils.get_asset(stac_item, asset_type=enum.AssetType.GEOTIFF)

        with tempfile.TemporaryDirectory() as d:
            file_path = utils.download_asset(asset=asset, save_directory=d)
            print("{0} has {1} bytes".format(os.path.basename(file_path), os.path.getsize(file_path)))

    def test_download_href(self):
        stac_id = "20190829T173549Z_1799_POM1_ST2_P"
        stac_item = client.search_one(stac_request=StacRequest(id=stac_id))
        asset = utils.get_asset(stac_item, asset_type=AssetType.THUMBNAIL)

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

            b = io.BytesIO()
            utils.download_asset(asset=asset, file_obj=b)
            data4 = b.read()
            self.assertEqual(data2, data4)


class TestPerf(unittest.TestCase):
    def test_query_limits(self):
        # Same geometry as above, but a wkt geometry instead of a geojson
        travis_wkt = "POLYGON((-97.9736 30.6251, -97.9188 30.6032, -97.9243 30.5703, -97.8695 30.5484, -97.8476 " \
                     "30.4717, -97.7764 30.4279, -97.5793 30.4991, -97.3711 30.4170, -97.4916 30.2089, " \
                     "-97.6505 30.0719, -97.6669 30.0665, -97.7107 30.0226, -98.1708 30.3567, -98.1270 30.4279, " \
                     "-98.0503 30.6251)) "
        geometry_data = GeometryData(wkt=travis_wkt,
                                     proj=ProjectionData(epsg=4326))

        limit = 200
        offset = 0
        total = 0
        while total < 1000:
            # make our request
            stac_request = StacRequest(intersects=geometry_data, limit=limit, offset=offset)
            # prepare request for next
            offset += limit
            for stac_item in client.search(stac_request):
                total += 1
                # do cool things with data here
            if total % limit == 0:
                print("stac item id: {0} at {1} index in request".format(stac_item.id, total))
        self.assertEqual(total, 1000)
