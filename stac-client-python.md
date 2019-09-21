
# gRPC stac-client-python
### What is this Good for
Use this library to access download information and other details for aerial imagery and for other geospatial datasets. This client accesses [Near Space Labs](https://nearspacelabs.com)' gRPC STAC service (or any gRPC STAC service). Landsat, NAIP and the Near Space Labs's Swift datasets are available for search.  

### Quick Code Example
Using a [StacRequest](https://geo-grpc.github.io/api/#epl.protobuf.StacRequest) query the service for one [StacItem](https://geo-grpc.github.io/api/#epl.protobuf.StacItem). Under the hood the client.search_one method uses the [StacService's](https://geo-grpc.github.io/api/#epl.protobuf.StacService) SearchOne gRPC method


```python
!pip freeze | grep nsl
```

    nsl.stac==0.2.5



```python
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest

stac_request = StacRequest(id='LE70380352019169EDC00')

# get a client interface to the gRPC channel
client = NSLClient()
# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)
print(stac_item)
```

    nsl client connecting to stac service at: localhost:10000
    
    id: "LE70380352019169EDC00"
    geometry {
      wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\013\000\000\000&\271i\3470\237\\\300\014]J\037b\301A@\215\227n\022\203\240\\\300V\237\253\255\330\267A@\215\227n\022\203 \\\300\264\310v\276\237\222A@)\314\366\0230 \\\300\"A\357;\304\224A@\360*%j\324\004\\\300\356;\241\373\221IB@\010\254\034Zd\003\\\300P\215\227n\022SB@Rf6\004\277\205\\\300\310\021wH\373xB@\366(\\\217\302\205\\\300\360\026HP\374xB@\013\312\004\350J\206\\\300\016\241\001\362#uB@\032x\271\\\025\207\\\300\230\340\226JnoB@&\271i\3470\237\\\300\014]J\037b\301A@"
      sr {
        wkid: 4326
      }
      simple: STRONG_SIMPLE
    }
    bbox {
      xmin: -114.508
      ymin: 35.1455
      xmax: -112.053
      ymax: 36.9452
      sr {
        wkid: 4326
      }
    }
    assets {
      key: "GEOTIFF_GCP_BLUE"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B1.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: BLUE
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B1.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_BQA"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_BQA.TIF"
        type: "image/vnd.stac.geotiff"
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_BQA.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_GREEN"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B2.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: GREEN
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B2.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_LWIR_1"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B6.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: LWIR_1
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B6.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_NIR"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B4.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: NIR
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B4.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_PAN"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B8.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: PAN
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B8.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_RED"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B3.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: RED
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B3.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_SWIR_1"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B5.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: SWIR_1
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B5.TIF"
      }
    }
    assets {
      key: "GEOTIFF_GCP_SWIR_2"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B7.TIF"
        type: "image/vnd.stac.geotiff"
        eo_bands: SWIR_2
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_B7.TIF"
      }
    }
    assets {
      key: "TXT_GCP_ANG"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_ANG.txt"
        type: "text/plain"
        asset_type: TXT
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_ANG.txt"
      }
    }
    assets {
      key: "TXT_GCP_MTL"
      value {
        href: "https://gcp-public-data-landsat.storage.googleapis.com/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_MTL.txt"
        type: "text/plain"
        asset_type: TXT
        cloud_platform: GCP
        bucket_manager: "Google"
        bucket_region: "us-multi-region"
        bucket: "gcp-public-data-landsat"
        object_path: "/LE07/01/038/035/LE07_L1TP_038035_20190618_20190618_01_RT/LE07_L1TP_038035_20190618_20190618_01_RT_MTL.txt"
      }
    }
    datetime {
      seconds: 1560880732
      nanos: 695231000
    }
    observed {
      seconds: 1560880732
      nanos: 695231000
    }
    updated {
      seconds: 1566935318
      nanos: 354185000
    }
    eo {
      platform: LANDSAT_7
      instrument: ETM
      constellation: LANDSAT
      gsd {
        value: 30.0
      }
      cloud_cover {
        value: 10.0
      }
    }
    landsat {
      scene_id: "LE70380352019169EDC00"
      product_id: "LE07_L1TP_038035_20190618_20190618_01_RT"
      processing_level: L1TP
      wrs_path: 38
      wrs_row: 35
    }
    



```python
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.geometry_pb2 import EnvelopeData, SpatialReferenceData
from nsl.stac.client import NSLClient

# define our area of interest bounds
utah_box = (-112.66342163085938, 37.738141282210385, -111.79824829101562, 38.44821130413263)
# here we define our envelope_data protobuf with bounds and a WGS-84 (`wkid=4326`) spatial reference
envelope_data = EnvelopeData(xmin=utah_box[0], 
                             ymin=utah_box[1], 
                             xmax=utah_box[2], 
                             ymax=utah_box[3],
                             sr=SpatialReferenceData(wkid=4326))
# Search for data that intersects the bounding box
stac_request = StacRequest(bbox=envelope_data)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item id: {}".format(stac_item.id))
```

    STAC item id: LC80370342019170LGN00
    STAC item id: LC80370332019170LGN00
    STAC item id: LE70380342019169EDC00
    STAC item id: LE70380332019169EDC00
    STAC item id: LE70370342019162EDC00
    STAC item id: LE70370332019162EDC00
    STAC item id: LC80380342019161LGN00
    STAC item id: LC80380332019161LGN00
    STAC item id: LC80370342019154LGN00
    STAC item id: LC80370332019154LGN00



```python
import json
import requests
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.geometry_pb2 import GeometryData, SpatialReferenceData

# request the geojson foot print of Lincoln County Nevada
r = requests.get("https://raw.githubusercontent.com/johan/world.geo.json/master/countries"
                 "/USA/NV/Lincoln.geo.json")
lincoln_geojson = json.dumps(r.json()['features'][0]['geometry'])
# create our GeometryData protobuf from geojson string and WGS-84 SpatialReferenceData protobuf
geometry_data = GeometryData(geojson=lincoln_geojson, 
                             sr=SpatialReferenceData(wkid=4326))
# Search for data that intersects the geojson geometry and limit results to 2 (instead of default of 10)
stac_request = StacRequest(geometry=geometry_data, limit=2)
# collect the ids from STAC items to compare against results from wkt GeometryData
geojson_ids = []

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item id: {}".format(stac_item.id))
    geojson_ids.append(stac_item.id)
```

    STAC item id: LE70380352019169EDC00
    STAC item id: LE70380342019169EDC00



```python
# Same geometry as above, but a wkt geometry instead of a geojson
lincoln_wkt = "MULTIPOLYGON (((-114.7057 38.6762,-114.0484 38.6762,-114.0484 38.5721,-114.0484 38.1504,"\
    "-114.0539 37.6027,-114.0484 37.0003,-114.0484 36.8414,-114.0813 36.8414,-115.8942 36.8414,"\
    "-115.8942 38.0518,-115.0014 38.0518,-115.0014 38.6762)))" 
geometry_data = GeometryData(wkt=lincoln_wkt, 
                             sr=SpatialReferenceData(wkid=4326))
stac_request = StacRequest(geometry=geometry_data, limit=2)
for stac_item in client.search(stac_request):
    print("STAC item id: {0} from wkt filter intersects result from geojson filter: {1}"
          .format(stac_item.id, stac_item.id in geojson_ids))
```

    STAC item id: LE70380352019169EDC00 from wkt filter intersects result from geojson filter: True
    STAC item id: LE70380342019169EDC00 from wkt filter intersects result from geojson filter: True



```python
from datetime import date, datetime, timezone
from nsl.stac.client import NSLClient
from nsl.stac import utils
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.query_pb2 import TimestampField, GT_OR_EQ

# the utils package has a helper for converting `date` or 
# `datetime` objects to google.protobuf.Timestamp protobufs
start_timestamp = utils.pb_timestamp(date(2017,1,1))
# make a filter that selects all data on or after January 1st, 2017
time_query = TimestampField(value=start_timestamp, rel_type=GT_OR_EQ)
stac_request = StacRequest(datetime=time_query, limit=2)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item date, {0}, is after {1}: {2}".format(
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(start_timestamp.seconds, tz=timezone.utc).isoformat(),
        stac_item.observed.seconds > start_timestamp.seconds))
```

    warning, no timezone provided with date, so UTC is assumed
    STAC item date, 2019-09-17T20:11:16+00:00, is after 2017-01-01T00:00:00+00:00: True
    STAC item date, 2019-09-17T17:43:15+00:00, is after 2017-01-01T00:00:00+00:00: True



```python
from datetime import datetime, timezone
from nsl.stac.client import NSLClient
from nsl.stac import utils
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.query_pb2 import TimestampField, BETWEEN
# Query data from January 1st, 2017 ...
start_timestamp = utils.pb_timestamp(datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
# ... up until January 1st, 2018
stop_timestamp = utils.pb_timestamp(datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
time_query = TimestampField(start=start_timestamp,
                            stop=stop_timestamp,
                            rel_type=BETWEEN)
stac_request = StacRequest(datetime=time_query, limit=2)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item date, {0}, is before {1}: {2}".format(
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(stop_timestamp.seconds, tz=timezone.utc).isoformat(),
        stac_item.observed.seconds < stop_timestamp.seconds))
```

    STAC item date, 2017-12-31T23:32:57+00:00, is before 2018-01-01T00:00:00+00:00: True
    STAC item date, 2017-12-31T23:31:22+00:00, is before 2018-01-01T00:00:00+00:00: True



```python
from datetime import datetime, timezone
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.geometry_pb2 import GeometryData, SpatialReferenceData
from epl.protobuf.query_pb2 import FloatField, LT_OR_EQ
from epl.protobuf.stac_pb2 import EoRequest, Eo

# create our ground sampling distance query to only return data less than or equal to 1 meter
gsd_query = FloatField(value=1.0, rel_type=LT_OR_EQ)
# create an eo_request container
eo_request = EoRequest(gsd=gsd_query)
# define ourselves a point in Fresno California
fresno_wkt = "POINT(-119.7871 36.7378)"
geometry_data = GeometryData(wkt=fresno_wkt, sr=SpatialReferenceData(wkid=4326))
# create a StacRequest with geometry, eo_request and a limit of 20
stac_request = StacRequest(geometry=geometry_data, eo=eo_request, limit=20)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("{0} STAC item '{1}' from {2}\nhas a gsd {3}, which should be less than or "
          "equal to requested gsd {4}: confirmed {5}".format(
        Eo.Constellation.Name(stac_item.eo.constellation),
        stac_item.id,
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        stac_item.eo.gsd.value,
        gsd_query.value,
        True))
```

    NAIP STAC item 'm_3611918_ne_11_h_20160629_20161004' from 2016-06-29T00:00:00+00:00
    has a gsd 0.6000000238418579, which should be less than or equal to requested gsd 1.0: confirmed True
    NAIP STAC item 'm_3611918_ne_11_1_20140619_20141113' from 2014-06-19T00:00:00+00:00
    has a gsd 1.0, which should be less than or equal to requested gsd 1.0: confirmed True
    NAIP STAC item 'm_3611918_ne_11_1_20120630_20120904' from 2012-06-30T00:00:00+00:00
    has a gsd 1.0, which should be less than or equal to requested gsd 1.0: confirmed True



```python
# SORT Direction
from datetime import date, datetime, timezone
from nsl.stac import utils
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.query_pb2 import TimestampField, LT, ASC

# the utils package has a helper for converting `date` or 
# `datetime` objects to google.protobuf.Timestamp protobufs
start_timestamp = utils.pb_timestamp(date(2017,1,1))
# make a filter that selects all data on or after January 1st, 2017
time_query = TimestampField(value=start_timestamp, rel_type=LT, sort_direction=ASC)
stac_request = StacRequest(datetime=time_query, limit=2)
client = NSLClient()
for stac_item in client.search(stac_request):
    print("Stac item date, {0}, is before {1}: {2}".format(
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(start_timestamp.seconds, tz=timezone.utc).isoformat(),
        stac_item.observed.seconds < start_timestamp.seconds))
```

    warning, no timezone provided with date, so UTC is assumed
    Stac item date, 1972-07-25T04:00:01+00:00, is before 2017-01-01T00:00:00+00:00: True
    Stac item date, 1972-07-25T04:00:26+00:00, is before 2017-01-01T00:00:00+00:00: True

