
# gRPC stac-client-python
### What is this Good for
Use this library to access download information and other details for aerial imagery and for other geospatial datasets. This client accesses [Near Space Labs](https://nearspacelabs.com)' gRPC STAC service (or any gRPC STAC service). Landsat, NAIP and the Near Space Labs's Swift datasets are available for search.  

### Quick Code Example
Using a [StacRequest](https://geo-grpc.github.io/api/#epl.protobuf.StacRequest) query the service for one [StacItem](https://geo-grpc.github.io/api/#epl.protobuf.StacItem). Under the hood the client.search_one method uses the [StacService's](https://geo-grpc.github.io/api/#epl.protobuf.StacService) SearchOne gRPC method





<details><summary>Python Code Sample</summary>


```python
from datetime import datetime
# the StacRequest is a protobuf message for making filter queries for data, you can think of it as 
# the query string in a url
from epl.protobuf.stac_pb2 import StacRequest
# the client package stubs out a little bit of the gRPC connection code 
from nsl.stac.client import NSLClient

# This search looks for any type of imagery hosted in the STAC service; anywhere in the world, at any 
# moment in time and of any data type
stac_request = StacRequest()

# get a client interface to the gRPC channel
client = NSLClient()
# search_one method requests only one item be returned that meets the query filters in the StacRequest 
# the item returned is a StacItem protobuf message
stac_item = client.search_one(stac_request)
# display the scene id
print("STAC item id {}".format(stac_item.id))

# display the observed date of the scene. The observed 
dt_observed = datetime.utcfromtimestamp(stac_item.observed.seconds)
print("Date observed {}".format(dt_observed.strftime("%m/%d/%Y, %H:%M:%S")))
```


</details>




<details><summary>Python Print-out</summary>


```text
    nsl client connecting to stac service at: localhost:10000
    
    STAC item id 20190917T201159Z_3_POM2_ST1
    Date observed 09/17/2019, 20:11:16
```


</details>



### What are Protobufs, gRPC, and Spatio Temporal Asset Catalogs? 
This python client library is used for connecting to a gRPC enabled STAC service. STAC items and STAC requests are Protocol Buffers (protobuf) instead of traditional JSON.

Never hear of gRPC, Protocol Buffers or STAC? Below are summary blurbs and links for more details about this open source projects.

Definition of STAC from https://stacspec.org/:
> The SpatioTemporal Asset Catalog (STAC) specification provides a common language to describe a range of geospatial information, so it can more easily be indexed and discovered.  A 'spatiotemporal asset' is any file that represents information about the earth captured in a certain space and time.

Definition of gRPC from https://grpc.io
> gRPC is a modern open source high performance RPC framework that can run in any environment. It can efficiently connect services in and across data centers with pluggable support for load balancing, tracing, health checking and authentication. It is also applicable in last mile of distributed computing to connect devices, mobile applications and browsers to backend services.

Definitions of Protocol Buffers (protobuf) from https://developers.google.com/protocol-buffers/
> Protocol buffers are Google's language-neutral, platform-neutral, extensible mechanism for serializing structured data – think XML, but smaller, faster, and simpler. You define how you want your data to be structured once, then you can use special generated source code to easily write and read your structured data to and from a variety of data streams and using a variety of languages.

In other words:
- You can think of Protobuf as strict a data format like xml or JSON + linting, except Protobuf is a compact binary message with strongly typed fields
- gRPC is similar to REST + OpenAPI, except gRPC is an [RPC](https://en.wikipedia.org/wiki/Remote_procedure_call) framework that supports bi-directional streaming
- STAC is a specification that helps remove repeated efforts for searching geospatial datasets (like WFS for specific data types)

### Setup
Grab it from [pip](https://pypi.org/project/nsl.stac/):
```bash
pip install nsl.stac
```

Install it from source:
```bash
pip install -r requirements.txt
python setup.py install
```

### Environment Variables
There are a few environment variables that the stac-client-python library relies on for accessing the STAC service:

- STAC_SERVICE, the address of the STAC service you connect to (defaults to "localhost:10000")

### Queries

#### Simple Query and the Makeup of a StacItem
There easiest query to construct is a `StacRequest` constructor with no variables, and the next simplest, is the case where we know the STAC item `id` that we want to search. If we already know the STAC `id` of an item, we can construct the `StacRequest` as follows:





<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
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
    
```


</details>



The above print out for the stac item is quite lengthy. Although `stac_item` is a protobuf object, it's `__str__` method prints out a JSON-like object. You can see in the below example that this `StacItem` contains the following:
- [GeometryData](https://geo-grpc.github.io/api/#epl.protobuf.GeometryData) which is defined with a WGS-84 well-known binary geometry
- [EnvelopeData](https://geo-grpc.github.io/api/#epl.protobuf.EnvelopeData) which is also WGS-84
- [Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) Google's protobuf unix time format
- [Eo](https://geo-grpc.github.io/api/#epl.protobuf.Eo) for electro-optical sensor details
- [Landsat](https://geo-grpc.github.io/api/#epl.protobuf.Landsat) for Landsat sepcific details
- an array map of [StacItem.AssetsEntry](https://geo-grpc.github.io/api/#epl.protobuf.StacItem.AssetsEntry) with each [Asset](https://geo-grpc.github.io/api/#epl.protobuf.Asset) containing details about [AssetType](https://geo-grpc.github.io/api/#epl.protobuf.AssetType), Electro Optical [Band enums](https://geo-grpc.github.io/api/#epl.protobuf.Eo.Band) (if applicable), and other details for downloading and interpreting data

You may have notice that the [Asset](https://geo-grpc.github.io/api/#epl.protobuf.Asset) in the above python print out has a number of additional parameters not included in the JSON STAC specification. 

#### Spatial Queries
The STAC specification has a bounding box `bbox` specification for STAC items. Here we make a STAC request using a bounding box. One slight difference from JSON STAC, is that we define an [EnvelopeData](https://geo-grpc.github.io/api/#epl.protobuf.EnvelopeData) protobuf object. This allows us to use other projections besides WGS84





<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
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
```


</details>



Above should be printed the STAC ids of 10 items (10 is the default limit for the service we connected to).

Next we want to try searching by geometry instead of bounding box. We'll use a geojson to define our [GeometryData](https://geo-grpc.github.io/api/#epl.protobuf.GeometryData) protobuf. GeometryData can be defined using geojson, wkt, wkb, or esrishape:





<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
    STAC item id: LE70380352019169EDC00
    STAC item id: LE70380342019169EDC00
```


</details>



Same geometry as above, but a wkt geometry instead of a geojson:





<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
    STAC item id: LE70380352019169EDC00 from wkt filter intersects result from geojson filter: True
    STAC item id: LE70380342019169EDC00 from wkt filter intersects result from geojson filter: True
```


</details>



### Temporal Queries
When it comes to Temporal queries there are a few things to note. One is that we are using Google's [Timestamp proto](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) to define the temporal aspect of STAC items. This means time is stored with a `int64` for seconds and a `int32` for nanoseconds relative to an epoch at UTC midnight on January 1, 1970.

So when you read the time fields on a [StacItem](https://geo-grpc.github.io/api/#epl.protobuf.StacItem), you'll notice that `datetime`, `observed`, `updated`, and `processed` all use the Timestamp Protobuf object.

When creating a time query filter, we want to use the >, >=, <, <=, ==, != operations and inclusive and exclusive range requests. We do this by using a [TimestampField](https://geo-grpc.github.io/api/#epl.protobuf.TimestampField), where we define the value using the `value` field or the `start`&`stop` fields. And then we define a relationship type using the `rel_type` field and the [FieldRelationship](https://geo-grpc.github.io/api/#epl.protobuf.FieldRelationship) enum values of `EQ`, `LT_OR_EQ`, `GT_OR_EQ`, `LT`, `GT`, `BETWEEN`, `NOT_BETWEEN`, or `NOT_EQ`.





<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
    STAC item date, 2019-09-17T20:11:16+00:00, is after 2017-01-01T00:00:00+00:00: True
    STAC item date, 2019-09-17T17:43:15+00:00, is after 2017-01-01T00:00:00+00:00: True
```


</details>



The above result shows the datetime of the STAC item, the datetime of the query and a confirmation that they satisfy the query filter. Notice the warning, this is because our date doesn't have a timezone associated with it. By default we assume UTC.

Now we're going to do a range request and select data between two dates:





<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
    STAC item date, 2017-12-31T23:32:57+00:00, is before 2018-01-01T00:00:00+00:00: True
    STAC item date, 2017-12-31T23:31:22+00:00, is before 2018-01-01T00:00:00+00:00: True
```


</details>



In the above print out we are returned STAC items that are between the dates of Jan 1 2017 and Jan 1 2018. Also, notice there's no warnings as we defined our utc timezone on the datetime objects.

### Queries on Parameters Besides the Spatio-Temporal
Proto3, the version of proto definition used for gRPC STAC, creates messages that are similar to structs in C. One of the drawbacks to structs is that for floats, integers, enums and booleans all fields that are not set are initialized to a value of zero. In geospatial sciences, defaulting to zero can cause problems in that an algorithm or user might interpret that as a true value. 

To get around this, Google uses wrappers for floats and ints and some of those are used in gRPC STAC. For example, some of the fields like `off_nadir`, `azimuth` and others in the Electro Optical protobuf message, [Eo](https://geo-grpc.github.io/api/#epl.protobuf.Eo) use the `google.protobuf.FloatValue` wrapper. As a consequence, accessing those values requires calling `field_name.value` instead of `field_name` to access the data.

For our ground sampling distance query we're using another query filter; this time it's the [FloatField](https://geo-grpc.github.io/api/#epl.protobuf.FloatField). It behaves just as the TimestampField, but with floats for `value` or for `start`&`stop`.

In order to make our ground sampling query we need to insert it inside of an [EoRequest](https://geo-grpc.github.io/api/#epl.protobuf.EoRequest) container and set that to the `eo` field of the `StacRequest`.






<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
    NAIP STAC item 'm_3611918_ne_11_h_20160629_20161004' from 2016-06-29T00:00:00+00:00
    has a gsd 0.6000000238418579, which should be less than or equal to requested gsd 1.0: confirmed True
    NAIP STAC item 'm_3611918_ne_11_1_20140619_20141113' from 2014-06-19T00:00:00+00:00
    has a gsd 1.0, which should be less than or equal to requested gsd 1.0: confirmed True
    NAIP STAC item 'm_3611918_ne_11_1_20120630_20120904' from 2012-06-30T00:00:00+00:00
    has a gsd 1.0, which should be less than or equal to requested gsd 1.0: confirmed True
```


</details>



Notice that gsd has some extra float errors for the item `m_3611918_ne_11_h_20160629_20161004`. This is because the FloatValue is a float32, but numpy want's all number to be as large and precise as possible. So there's some scrambled mess at the end of the precision of gsd.

Also, even though we set the `limit` to 20, the print out only returns 3 values. That's because the STAC service we're using only holds NAIP and Landsat data for Fresno California. And for NAIP there are only 3 different surveys with 1 meter or higher resolution for that location.

We can also apply a sort direction to our results so that they are ascending or decending. In the below sample we search all data before 2017 starting with the oldest results first by specifiying the `ASC`, ascending parameter.





<details><summary>Python Code Sample</summary>


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


</details>




<details><summary>Python Print-out</summary>


```text
    Stac item date, 1972-07-25T04:00:01+00:00, is before 2017-01-01T00:00:00+00:00: True
    Stac item date, 1972-07-25T04:00:26+00:00, is before 2017-01-01T00:00:00+00:00: True
```


</details>



### Downloading
To download an asset use the `bucket` + `object_path` or the `href` fields from the asset, and download the data using the library of your choice. There is also a download utility in the `nsl.stac.utils` module. Downloading from Google Cloud Storage buckets requires having defined your `GOOGLE_APPLICATION_CREDENTIALS` [environment variable](https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable). Downloading from AWS/S3 requires having your configuration file or environment variables defined as you would for [boto3](https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/quickstart.html#configuration). To downlad an asset follow the pattern in the below example:





<details><summary>Python Code Sample</summary>


```python
import tempfile
from nsl.stac.client import NSLClient
from nsl.stac import utils
from epl.protobuf.stac_pb2 import StacRequest

stac_request = StacRequest(id='LE70380352019169EDC00')

# get a client interface to the gRPC channel
client = NSLClient()
# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)

asset = stac_item.assets['TXT_GCP_MTL']
with tempfile.TemporaryFile() as file_obj:
    utils.download_asset(asset=asset, file_obj=file_obj)
    text_d = file_obj.read().decode('ascii')
    print(text_d)
```


</details>




<details><summary>Python Print-out</summary>


```text
    GROUP = L1_METADATA_FILE
      GROUP = METADATA_FILE_INFO
        ORIGIN = "Image courtesy of the U.S. Geological Survey"
        REQUEST_ID = "0501906188198_00004"
        LANDSAT_SCENE_ID = "LE70380352019169EDC00"
        LANDSAT_PRODUCT_ID = "LE07_L1TP_038035_20190618_20190618_01_RT"
        COLLECTION_NUMBER = 01
        FILE_DATE = 2019-06-18T19:06:33Z
        STATION_ID = "EDC"
        PROCESSING_SOFTWARE_VERSION = "LPGS_13.1.0"
        DATA_CATEGORY = "NOMINAL"
      END_GROUP = METADATA_FILE_INFO
      GROUP = PRODUCT_METADATA
        DATA_TYPE = "L1TP"
        COLLECTION_CATEGORY = "RT"
        ELEVATION_SOURCE = "GLS2000"
        OUTPUT_FORMAT = "GEOTIFF"
        EPHEMERIS_TYPE = "PREDICTIVE"
        SPACECRAFT_ID = "LANDSAT_7"
        SENSOR_ID = "ETM"
        SENSOR_MODE = "BUMPER"
        WRS_PATH = 038
        WRS_ROW = 035
        DATE_ACQUIRED = 2019-06-18
        SCENE_CENTER_TIME = "17:58:52.6952310Z"
        CORNER_UL_LAT_PRODUCT = 37.00640
        CORNER_UL_LON_PRODUCT = -114.76125
        CORNER_UR_LAT_PRODUCT = 37.06211
        CORNER_UR_LON_PRODUCT = -111.96733
        CORNER_LL_LAT_PRODUCT = 35.03877
        CORNER_LL_LON_PRODUCT = -114.66875
        CORNER_LR_LAT_PRODUCT = 35.09062
        CORNER_LR_LON_PRODUCT = -111.94348
        CORNER_UL_PROJECTION_X_PRODUCT = 165300.000
        CORNER_UL_PROJECTION_Y_PRODUCT = 4102200.000
        CORNER_UR_PROJECTION_X_PRODUCT = 414000.000
        CORNER_UR_PROJECTION_Y_PRODUCT = 4102200.000
        CORNER_LL_PROJECTION_X_PRODUCT = 165300.000
        CORNER_LL_PROJECTION_Y_PRODUCT = 3883500.000
        CORNER_LR_PROJECTION_X_PRODUCT = 414000.000
        CORNER_LR_PROJECTION_Y_PRODUCT = 3883500.000
        PANCHROMATIC_LINES = 14581
        PANCHROMATIC_SAMPLES = 16581
        REFLECTIVE_LINES = 7291
        REFLECTIVE_SAMPLES = 8291
        THERMAL_LINES = 7291
        THERMAL_SAMPLES = 8291
        FILE_NAME_BAND_1 = "LE07_L1TP_038035_20190618_20190618_01_RT_B1.TIF"
        FILE_NAME_BAND_2 = "LE07_L1TP_038035_20190618_20190618_01_RT_B2.TIF"
        FILE_NAME_BAND_3 = "LE07_L1TP_038035_20190618_20190618_01_RT_B3.TIF"
        FILE_NAME_BAND_4 = "LE07_L1TP_038035_20190618_20190618_01_RT_B4.TIF"
        FILE_NAME_BAND_5 = "LE07_L1TP_038035_20190618_20190618_01_RT_B5.TIF"
        FILE_NAME_BAND_6_VCID_1 = "LE07_L1TP_038035_20190618_20190618_01_RT_B6_VCID_1.TIF"
        FILE_NAME_BAND_6_VCID_2 = "LE07_L1TP_038035_20190618_20190618_01_RT_B6_VCID_2.TIF"
        FILE_NAME_BAND_7 = "LE07_L1TP_038035_20190618_20190618_01_RT_B7.TIF"
        FILE_NAME_BAND_8 = "LE07_L1TP_038035_20190618_20190618_01_RT_B8.TIF"
        FILE_NAME_BAND_QUALITY = "LE07_L1TP_038035_20190618_20190618_01_RT_BQA.TIF"
        GROUND_CONTROL_POINT_FILE_NAME = "LE07_L1TP_038035_20190618_20190618_01_RT_GCP.txt"
        ANGLE_COEFFICIENT_FILE_NAME = "LE07_L1TP_038035_20190618_20190618_01_RT_ANG.txt"
        METADATA_FILE_NAME = "LE07_L1TP_038035_20190618_20190618_01_RT_MTL.txt"
        CPF_NAME = "LE07CPF_20190401_20190630_01.06"
      END_GROUP = PRODUCT_METADATA
      GROUP = IMAGE_ATTRIBUTES
        CLOUD_COVER = 10.00
        CLOUD_COVER_LAND = 10.00
        IMAGE_QUALITY = 9
        SUN_AZIMUTH = 114.88805154
        SUN_ELEVATION = 65.79784674
        EARTH_SUN_DISTANCE = 1.0160252
        SATURATION_BAND_1 = "Y"
        SATURATION_BAND_2 = "Y"
        SATURATION_BAND_3 = "Y"
        SATURATION_BAND_4 = "Y"
        SATURATION_BAND_5 = "Y"
        SATURATION_BAND_6_VCID_1 = "N"
        SATURATION_BAND_6_VCID_2 = "Y"
        SATURATION_BAND_7 = "N"
        SATURATION_BAND_8 = "N"
        GROUND_CONTROL_POINTS_VERSION = 4
        GROUND_CONTROL_POINTS_MODEL = 126
        GEOMETRIC_RMSE_MODEL = 4.600
        GEOMETRIC_RMSE_MODEL_Y = 3.958
        GEOMETRIC_RMSE_MODEL_X = 2.344
      END_GROUP = IMAGE_ATTRIBUTES
      GROUP = MIN_MAX_RADIANCE
        RADIANCE_MAXIMUM_BAND_1 = 293.700
        RADIANCE_MINIMUM_BAND_1 = -6.200
        RADIANCE_MAXIMUM_BAND_2 = 300.900
        RADIANCE_MINIMUM_BAND_2 = -6.400
        RADIANCE_MAXIMUM_BAND_3 = 234.400
        RADIANCE_MINIMUM_BAND_3 = -5.000
        RADIANCE_MAXIMUM_BAND_4 = 241.100
        RADIANCE_MINIMUM_BAND_4 = -5.100
        RADIANCE_MAXIMUM_BAND_5 = 47.570
        RADIANCE_MINIMUM_BAND_5 = -1.000
        RADIANCE_MAXIMUM_BAND_6_VCID_1 = 17.040
        RADIANCE_MINIMUM_BAND_6_VCID_1 = 0.000
        RADIANCE_MAXIMUM_BAND_6_VCID_2 = 12.650
        RADIANCE_MINIMUM_BAND_6_VCID_2 = 3.200
        RADIANCE_MAXIMUM_BAND_7 = 16.540
        RADIANCE_MINIMUM_BAND_7 = -0.350
        RADIANCE_MAXIMUM_BAND_8 = 243.100
        RADIANCE_MINIMUM_BAND_8 = -4.700
      END_GROUP = MIN_MAX_RADIANCE
      GROUP = MIN_MAX_REFLECTANCE
        REFLECTANCE_MAXIMUM_BAND_1 = 0.467827
        REFLECTANCE_MINIMUM_BAND_1 = -0.009876
        REFLECTANCE_MAXIMUM_BAND_2 = 0.525779
        REFLECTANCE_MINIMUM_BAND_2 = -0.011183
        REFLECTANCE_MAXIMUM_BAND_3 = 0.498479
        REFLECTANCE_MINIMUM_BAND_3 = -0.010633
        REFLECTANCE_MAXIMUM_BAND_4 = 0.730073
        REFLECTANCE_MINIMUM_BAND_4 = -0.015443
        REFLECTANCE_MAXIMUM_BAND_5 = 0.696181
        REFLECTANCE_MINIMUM_BAND_5 = -0.014635
        REFLECTANCE_MAXIMUM_BAND_7 = 0.659301
        REFLECTANCE_MINIMUM_BAND_7 = -0.013951
        REFLECTANCE_MAXIMUM_BAND_8 = 0.597722
        REFLECTANCE_MINIMUM_BAND_8 = -0.011556
      END_GROUP = MIN_MAX_REFLECTANCE
      GROUP = MIN_MAX_PIXEL_VALUE
        QUANTIZE_CAL_MAX_BAND_1 = 255
        QUANTIZE_CAL_MIN_BAND_1 = 1
        QUANTIZE_CAL_MAX_BAND_2 = 255
        QUANTIZE_CAL_MIN_BAND_2 = 1
        QUANTIZE_CAL_MAX_BAND_3 = 255
        QUANTIZE_CAL_MIN_BAND_3 = 1
        QUANTIZE_CAL_MAX_BAND_4 = 255
        QUANTIZE_CAL_MIN_BAND_4 = 1
        QUANTIZE_CAL_MAX_BAND_5 = 255
        QUANTIZE_CAL_MIN_BAND_5 = 1
        QUANTIZE_CAL_MAX_BAND_6_VCID_1 = 255
        QUANTIZE_CAL_MIN_BAND_6_VCID_1 = 1
        QUANTIZE_CAL_MAX_BAND_6_VCID_2 = 255
        QUANTIZE_CAL_MIN_BAND_6_VCID_2 = 1
        QUANTIZE_CAL_MAX_BAND_7 = 255
        QUANTIZE_CAL_MIN_BAND_7 = 1
        QUANTIZE_CAL_MAX_BAND_8 = 255
        QUANTIZE_CAL_MIN_BAND_8 = 1
      END_GROUP = MIN_MAX_PIXEL_VALUE
      GROUP = PRODUCT_PARAMETERS
        CORRECTION_GAIN_BAND_1 = "CPF"
        CORRECTION_GAIN_BAND_2 = "CPF"
        CORRECTION_GAIN_BAND_3 = "CPF"
        CORRECTION_GAIN_BAND_4 = "CPF"
        CORRECTION_GAIN_BAND_5 = "CPF"
        CORRECTION_GAIN_BAND_6_VCID_1 = "CPF"
        CORRECTION_GAIN_BAND_6_VCID_2 = "CPF"
        CORRECTION_GAIN_BAND_7 = "CPF"
        CORRECTION_GAIN_BAND_8 = "CPF"
        CORRECTION_BIAS_BAND_1 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_2 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_3 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_4 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_5 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_6_VCID_1 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_6_VCID_2 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_7 = "INTERNAL_CALIBRATION"
        CORRECTION_BIAS_BAND_8 = "INTERNAL_CALIBRATION"
        GAIN_BAND_1 = "L"
        GAIN_BAND_2 = "L"
        GAIN_BAND_3 = "L"
        GAIN_BAND_4 = "L"
        GAIN_BAND_5 = "L"
        GAIN_BAND_6_VCID_1 = "L"
        GAIN_BAND_6_VCID_2 = "H"
        GAIN_BAND_7 = "L"
        GAIN_BAND_8 = "L"
        GAIN_CHANGE_BAND_1 = "LL"
        GAIN_CHANGE_BAND_2 = "LL"
        GAIN_CHANGE_BAND_3 = "LL"
        GAIN_CHANGE_BAND_4 = "LL"
        GAIN_CHANGE_BAND_5 = "LL"
        GAIN_CHANGE_BAND_6_VCID_1 = "LL"
        GAIN_CHANGE_BAND_6_VCID_2 = "HH"
        GAIN_CHANGE_BAND_7 = "LL"
        GAIN_CHANGE_BAND_8 = "LL"
        GAIN_CHANGE_SCAN_BAND_1 = 0
        GAIN_CHANGE_SCAN_BAND_2 = 0
        GAIN_CHANGE_SCAN_BAND_3 = 0
        GAIN_CHANGE_SCAN_BAND_4 = 0
        GAIN_CHANGE_SCAN_BAND_5 = 0
        GAIN_CHANGE_SCAN_BAND_6_VCID_1 = 0
        GAIN_CHANGE_SCAN_BAND_6_VCID_2 = 0
        GAIN_CHANGE_SCAN_BAND_7 = 0
        GAIN_CHANGE_SCAN_BAND_8 = 0
      END_GROUP = PRODUCT_PARAMETERS
      GROUP = RADIOMETRIC_RESCALING
        RADIANCE_MULT_BAND_1 = 1.1807E+00
        RADIANCE_MULT_BAND_2 = 1.2098E+00
        RADIANCE_MULT_BAND_3 = 9.4252E-01
        RADIANCE_MULT_BAND_4 = 9.6929E-01
        RADIANCE_MULT_BAND_5 = 1.9122E-01
        RADIANCE_MULT_BAND_6_VCID_1 = 6.7087E-02
        RADIANCE_MULT_BAND_6_VCID_2 = 3.7205E-02
        RADIANCE_MULT_BAND_7 = 6.6496E-02
        RADIANCE_MULT_BAND_8 = 9.7559E-01
        RADIANCE_ADD_BAND_1 = -7.38071
        RADIANCE_ADD_BAND_2 = -7.60984
        RADIANCE_ADD_BAND_3 = -5.94252
        RADIANCE_ADD_BAND_4 = -6.06929
        RADIANCE_ADD_BAND_5 = -1.19122
        RADIANCE_ADD_BAND_6_VCID_1 = -0.06709
        RADIANCE_ADD_BAND_6_VCID_2 = 3.16280
        RADIANCE_ADD_BAND_7 = -0.41650
        RADIANCE_ADD_BAND_8 = -5.67559
        REFLECTANCE_MULT_BAND_1 = 1.8807E-03
        REFLECTANCE_MULT_BAND_2 = 2.1140E-03
        REFLECTANCE_MULT_BAND_3 = 2.0044E-03
        REFLECTANCE_MULT_BAND_4 = 2.9351E-03
        REFLECTANCE_MULT_BAND_5 = 2.7985E-03
        REFLECTANCE_MULT_BAND_7 = 2.6506E-03
        REFLECTANCE_MULT_BAND_8 = 2.3987E-03
        REFLECTANCE_ADD_BAND_1 = -0.011757
        REFLECTANCE_ADD_BAND_2 = -0.013297
        REFLECTANCE_ADD_BAND_3 = -0.012637
        REFLECTANCE_ADD_BAND_4 = -0.018378
        REFLECTANCE_ADD_BAND_5 = -0.017433
        REFLECTANCE_ADD_BAND_7 = -0.016602
        REFLECTANCE_ADD_BAND_8 = -0.013955
      END_GROUP = RADIOMETRIC_RESCALING
      GROUP = THERMAL_CONSTANTS
        K1_CONSTANT_BAND_6_VCID_1 = 666.09
        K2_CONSTANT_BAND_6_VCID_1 = 1282.71
        K1_CONSTANT_BAND_6_VCID_2 = 666.09
        K2_CONSTANT_BAND_6_VCID_2 = 1282.71
      END_GROUP = THERMAL_CONSTANTS
      GROUP = PROJECTION_PARAMETERS
        MAP_PROJECTION = "UTM"
        DATUM = "WGS84"
        ELLIPSOID = "WGS84"
        UTM_ZONE = 12
        GRID_CELL_SIZE_PANCHROMATIC = 15.00
        GRID_CELL_SIZE_REFLECTIVE = 30.00
        GRID_CELL_SIZE_THERMAL = 30.00
        ORIENTATION = "NORTH_UP"
        RESAMPLING_OPTION = "CUBIC_CONVOLUTION"
        SCAN_GAP_INTERPOLATION = 2.0
      END_GROUP = PROJECTION_PARAMETERS
    END_GROUP = L1_METADATA_FILE
    END
    
```


</details>



## Differences between gRPC+Protobuf STAC and OpenAPI+JSON STAC
If you are already familiar with STAC, you'll need to know that gRPC + Protobuf STAC is slightly different from the JSON definitions. 

JSON is naturally a flexible format and with linters you can force it to adhere to rules. Protobuf is a strict data format and that required a few differences between the JSON STAC specification and the protobuf specification:

### JSON STAC Compared with Protobuf STAC

#### STAC Item Comparison
For Comparison, here is the [JSON STAC item field summary](https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md#item-fields) and the [Protobuf STAC item field summary](https://geo-grpc.github.io/api/#epl.protobuf.StacItem). Below is a table comparing the two:


|  Field Name 	| STAC Protobuf Type                                                                                                       	| STAC JSON Type                                                             	|
|-------------	|--------------------------------------------------------------------------------------------------------------------------	|----------------------------------------------------------------------------	|
| id          	| [string](https://geo-grpc.github.io/api/#string)                                                                         	| string                                                                     	|
| type        	| NA                                                                                                                       	| string                                                                     	|
| geometry    	| [GeometryData](https://geo-grpc.github.io/api/#epl.protobuf.GeometryData)                                                	| [GeoJSON Geometry Object](https://tools.ietf.org/html/rfc7946#section-3.1) 	|
| bbox        	| [EnvelopeData](https://geo-grpc.github.io/api/#epl.protobuf.EnvelopeData)                                                	| [number]                                                                   	|
| properties  	| [google.protobuf.Any](https://developers.google.com/protocol-buffers/docs/proto3#any)                                               	| Properties Object                                                          	|
| links       	| NA                                                                                                                       	| [Link Object]                                                              	|
| assets      	| [StacItem.AssetsEntry](https://geo-grpc.github.io/api/#epl.protobuf.StacItem.AssetsEntry)                                	| Map                                                                        	|
| collection  	| [string](https://geo-grpc.github.io/api/#string)                                                                         	| string                                                                     	|
| title       	| [string](https://geo-grpc.github.io/api/#string)                                                                         	| Inside Properties                                                          	|
| datetime    	| [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) 	| Inside Properties                                                          	|
| observation 	| [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) 	| Inside Properties                                                          	|
| processed   	| [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) 	| Inside Properties                                                          	|
| updated     	| [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) 	| Inside Properties                                                          	|
| duration    	| [google.protobuf.Duration](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/duration.proto)   	| Inside Properties                                                          	|
| eo          	| [Eo](https://geo-grpc.github.io/api/#epl.protobuf.Eo)                                                                    	| Inside Properties                                                          	|
| sar         	| [Sar](https://geo-grpc.github.io/api/#epl.protobuf.Sar)                                                                  	| Inside Properties                                                          	|
| landsat     	| [Landsat](https://geo-grpc.github.io/api/#epl.protobuf.Landsat)                                                          	| Inside Properties                                                          	|


#### Eo Comparison
For Comparison, here is the [JSON STAC Electro Optical field summary](https://github.com/radiantearth/stac-spec/tree/master/extensions/eo#item-fields) and the [Protobuf STAC Electro Optical field summary](https://geo-grpc.github.io/api/#epl.protobuf.Eo). Below is a table comparing the two:

| JSON Field Name  	| JSON Data Type 	| Protobuf Field Name 	| Protobuf Data Type                  	|
|------------------	|----------------	|---------------------	|-------------------------------------	|
| eo:gsd           	| number         	| gsd                 	| [google.protobuf.wrappers.FloatValue](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto) 	|
| eo:platform      	| string         	| platform            	| [Eo.Platform](https://geo-grpc.github.io/api/#epl.protobuf.Eo.Platform)                         	|
| eo:instrument    	| string         	| instrument          	| [Eo.Instrument](https://geo-grpc.github.io/api/#epl.protobuf.Eo.Instrument)                       	|
| eo:constellation 	| string         	| constellation       	| [Eo.Constellation](https://geo-grpc.github.io/api/#epl.protobuf.Eo.Platform)                    	|
| eo:bands         	| [Band Object](https://github.com/radiantearth/stac-spec/tree/master/extensions/eo#band-object)  	| bands               	| [Eo.Band](https://geo-grpc.github.io/api/#epl.protobuf.Eo.Band)                             	|
| eo:epsg          	| integer        	| epsg                	| uint32                              	|
| eo:cloud_cover   	| number         	| cloud_cover         	| [google.protobuf.wrappers.FloatValue](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto) 	|
| eo:off_nadir     	| number         	| off_nadir           	| [google.protobuf.wrappers.FloatValue](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto) 	|
| eo:azimuth       	| number         	| azimuth             	| [google.protobuf.wrappers.FloatValue](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto) 	|
| eo:sun_azimuth   	| number         	| sun_azimuth         	| [google.protobuf.wrappers.FloatValue](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto) 	|
| eo:sun_elevation 	| number         	| sun_elevation       	| [google.protobuf.wrappers.FloatValue](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto) 	|


### Updating the samples in this README
Use this Jupyter Notebook to update the README.md. Do not directly edit the README.md. It will be overwritten by output from `ipynb2md.py`. First edit this README.ipynb, in kernel Restart & Run All to confirm your changes worked, Save and Checkpoint, then run the python script `python ipynb2md.py`.

