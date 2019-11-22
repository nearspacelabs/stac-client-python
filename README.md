
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
    nsl client connecting to stac service at: eap.nearspacelabs.net:9090
    
    STAC item id 20191110T005417Z_1594_ST2_POM1
    Date observed 08/29/2019, 17:28:57
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
You'll need to have Python3 installed (does not work with Python2). If you've got multiple versions of Python and pip, you may need to use `python3` and `pip3` in the below installation commands.
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

- STAC_SERVICE, the address of the STAC service you connect to (defaults to "eap.nearspacelabs.net:9090")
- NSL_ID and NSL_SECRET, if you're downloading Near Space Labs data you'll need credentials
- GOOGLE_APPLICATION_CREDENTIALS, if you're downloading open data hosted on Google Cloud

### How to Use the Jupyter Notebook

Install the requirements for the demo:

```bash

pip install -r requirements-demo.txt

```

Run Jupyter notebook with your environment variables set for `NSL_ID` and `NSL_SECRET`:

```bash

NSL_ID="YOUR_ID" NSL_SECRET="YOUR_SECRET" jupyter notebook

```

### Queries

#### Simple Query and the Makeup of a StacItem
There easiest query to construct is a `StacRequest` constructor with no variables, and the next simplest, is the case where we know the STAC item `id` that we want to search. If we already know the STAC `id` of an item, we can construct the `StacRequest` as follows:





<details><summary>Python Code Sample</summary>


```python
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest

stac_request = StacRequest(id='20191122T130410Z_640_ST2_POM1')

# get a client interface to the gRPC channel
client = NSLClient()
# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)
print(stac_item)
```


</details>




<details><summary>Python Print-out</summary>


```text
    id: "20191122T130410Z_640_ST2_POM1"
    geometry {
      wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000C\266Yx+\372\353?1P\326\r\325\326D@\346\336&\0277\370\354?8[E\270\347\326D@\221\273\010.j\363\354?\330`\274T7\331D@\346\244&fL\365\353?3\037J\247$\331D@C\266Yx+\372\353?1P\326\r\325\326D@"
      sr {
        wkid: 4326
      }
      simple: STRONG_SIMPLE
    }
    bbox {
      xmin: 0.8736936564575017
      ymin: 41.67837689365877
      xmax: 0.9052997066673611
      ymax: 41.69700106809768
      sr {
        wkid: 4326
      }
    }
    properties {
      type_url: "type.googleapis.com/st.protobuf.SwiftMetadata"
      value: "\n\02720190412T110321Z_LLEIDA\022 4720b2613dc9377a70e74076acb739cf\032\03120191122T125836Z_SWIFTERA \01022\032+POINT(0.8811652660369873 41.69331741333008):\003\010\346!:\005\r|\320ZFB\003 \200\005R\03520190720T055416Z_640_POM2_ST1Z\0012Z\0010Z\0011Z\0019Z\0010Z\0014Z\0011Z\0012Z\001TZ\0011Z\0012Z\0011Z\0016Z\0010Z\0012Z\001ZZ\001_Z\0016Z\0011Z\0017Z\0013Z\001_Z\001PZ\001OZ\001MZ\0011Z\001_Z\001SZ\001TZ\0012Z\0012Z\0010Z\0011Z\0019Z\0010Z\0017Z\0012Z\0010Z\001TZ\0010Z\0015Z\0015Z\0012Z\0014Z\0012Z\001ZZ\001_Z\0016Z\0014Z\0010Z\001_Z\001PZ\001OZ\001MZ\0012Z\001_Z\001SZ\001TZ\0011Z\03520190720T055416Z_640_POM2_ST1b\03620190412T121602Z_6173_POM1_ST2h\001p\001\200\001\215\010\210\001\271\316\t"
    }
    assets {
      key: "GEOTIFF_RGB"
      value {
        href: "https://eap.nearspacelabs.net/download/20191122T125836Z_SWIFTERA/Publish_0/20191122T130410Z_640_ST2_POM1.tif"
        type: "image/vnd.stac.geotiff"
        eo_bands: RGB
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Swiftera"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20191122T125836Z_SWIFTERA/Publish_0/20191122T130410Z_640_ST2_POM1.tif"
      }
    }
    assets {
      key: "THUMBNAIL_RGB"
      value {
        href: "https://eap.nearspacelabs.net/download/20191122T125836Z_SWIFTERA/Publish_0/20191122T130410Z_640_ST2_POM1_thumb.jpg"
        type: "image/jpeg"
        eo_bands: RGB
        asset_type: THUMBNAIL
        cloud_platform: GCP
        bucket_manager: "Swiftera"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20191122T125836Z_SWIFTERA/Publish_0/20191122T130410Z_640_ST2_POM1_thumb.jpg"
      }
    }
    datetime {
      seconds: 1555071362
      nanos: 539381000
    }
    observed {
      seconds: 1555071362
      nanos: 539381000
    }
    processed {
      seconds: 1574427850
      nanos: 111098000
    }
    updated {
      seconds: 1574427850
      nanos: 859065942
    }
    eo {
      platform: SWIFT_2
      instrument: POM_1
      constellation: SWIFT
      sun_azimuth {
        value: 188.4600067138672
      }
      sun_elevation {
        value: 56.741512298583984
      }
      azimuth {
        value: -100.5069351196289
      }
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
neighborhood_box = (-97.73294577459876, 30.251945643016235, -97.71732458929603, 30.264548996109724)
# here we define our envelope_data protobuf with bounds and a WGS-84 (`wkid=4326`) spatial reference
envelope_data = EnvelopeData(xmin=neighborhood_box[0], 
                             ymin=neighborhood_box[1], 
                             xmax=neighborhood_box[2], 
                             ymax=neighborhood_box[3],
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
    STAC item id: 20191110T003517Z_1594_ST2_POM1
    STAC item id: 20191121T182921Z_1594_ST2_POM1
    STAC item id: 20191121T201211Z_1594_ST2_POM1
    STAC item id: 20191121T192629Z_1594_ST2_POM1
    STAC item id: 20191111T193822Z_1594_ST2_POM1
    STAC item id: 20191121T174541Z_1594_ST2_POM1
    STAC item id: 20191122T130151Z_1594_ST2_POM1
    STAC item id: 20191110T002000Z_1594_ST2_POM1
    STAC item id: 20191110T004641Z_1594_ST2_POM1
    STAC item id: 20191110T005417Z_1594_ST2_POM1
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

# request the geojson foot print of Travis County, Texas
r = requests.get("https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/TX/Travis.geo.json")
travis_geojson = json.dumps(r.json()['features'][0]['geometry'])
# create our GeometryData protobuf from geojson string and WGS-84 SpatialReferenceData protobuf
geometry_data = GeometryData(geojson=travis_geojson, 
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
    STAC item id: 20191110T003517Z_1594_ST2_POM1
    STAC item id: 20191110T002000Z_1594_ST2_POM1
```


</details>



Same geometry as above, but a wkt geometry instead of a geojson:





<details><summary>Python Code Sample</summary>


```python
# Same geometry as above, but a wkt geometry instead of a geojson
travis_wkt = "POLYGON((-97.9736 30.6251, -97.9188 30.6032, -97.9243 30.5703, -97.8695 30.5484, -97.8476 30.4717, -97.7764 30.4279, -97.5793 30.4991, -97.3711 30.4170, -97.4916 30.2089, -97.6505 30.0719, -97.6669 30.0665, -97.7107 30.0226, -98.1708 30.3567, -98.1270 30.4279, -98.0503 30.6251))" 
geometry_data = GeometryData(wkt=travis_wkt, 
                             sr=SpatialReferenceData(wkid=4326))
stac_request = StacRequest(geometry=geometry_data, limit=2)
for stac_item in client.search(stac_request):
    print("STAC item id: {0} from wkt filter intersects result from geojson filter: {1}"
          .format(stac_item.id, stac_item.id in geojson_ids))
```


</details>




<details><summary>Python Print-out</summary>


```text
    STAC item id: 20191110T003517Z_1594_ST2_POM1 from wkt filter intersects result from geojson filter: True
    STAC item id: 20191110T002000Z_1594_ST2_POM1 from wkt filter intersects result from geojson filter: True
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
    STAC item date, 2019-08-29T17:28:57+00:00, is after 2017-01-01T00:00:00+00:00: True
    STAC item date, 2019-08-29T17:28:57+00:00, is after 2017-01-01T00:00:00+00:00: True
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
# Query data from August 1, 2019
start_timestamp = utils.pb_timestamp(datetime(2019, 8, 1, 0, 0, 0, tzinfo=timezone.utc))
# ... up until August 10, 2019
stop_timestamp = utils.pb_timestamp(datetime(2019, 8, 10, 0, 0, 0, tzinfo=timezone.utc))
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
    STAC item date, 2019-08-08T19:23:02+00:00, is before 2019-08-10T00:00:00+00:00: True
    STAC item date, 2019-08-08T19:23:02+00:00, is before 2019-08-10T00:00:00+00:00: True
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
# define ourselves a point in Austin, Texas
austin_capital_wkt = "POINT(-97.733333 30.266667)"
geometry_data = GeometryData(wkt=austin_capital_wkt, sr=SpatialReferenceData(wkid=4326))
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



Notice that gsd has some extra float errors for the item `m_3611918_ne_11_h_20160629_20161004`. This is because the FloatValue is a float32, but numpy want's all number to be as large and precise as possible. So there's some scrambled mess at the end of the precision of gsd.

Also, even though we set the `limit` to 20, the print out only returns 3 values. That's because the STAC service we're using only holds NAIP and Landsat data for Fresno California. And for NAIP there are only 3 different surveys with 1 meter or higher resolution for that location.

We can also apply a sort direction to our results so that they are ascending or decending. In the below sample we search all data before 2017 starting with the oldest results first by specifiying the `ASC`, ascending parameter. This is a complex query and can take a while.





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
start_timestamp = utils.pb_timestamp(date(2019, 8, 20))
# make a filter that selects all data on or after January 1st, 2017
time_query = TimestampField(value=start_timestamp, rel_type=LT, sort_direction=ASC)
stac_request = StacRequest(datetime=time_query, limit=2)
client = NSLClient()
for stac_item in client.search(stac_request):
    print("Stac item id {0}, date, {1}, is before {2}:{3}".format(
        stac_item.id,
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(start_timestamp.seconds, tz=timezone.utc).isoformat(),
        stac_item.observed.seconds < start_timestamp.seconds))
```


</details>




<details><summary>Python Print-out</summary>


```text
    Stac item id 20191122T130410Z_640_ST2_POM1, date, 2019-04-12T12:16:02+00:00, is before 2019-08-20T00:00:00+00:00:True
    Stac item id 20191122T130408Z_641_ST2_POM1, date, 2019-04-12T12:16:15+00:00, is before 2019-08-20T00:00:00+00:00:True
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

stac_request = StacRequest(id='20191122T130410Z_640_ST2_POM1')

# get a client interface to the gRPC channel
client = NSLClient()
# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)

asset = stac_item.assets['THUMBNAIL_RGB']
with tempfile.NamedTemporaryFile() as file_obj:
    utils.download_asset(asset=asset, save_filename=file_obj.name)
```


</details>




<details><summary>Python Print-out</summary>


```text
    saving to filename...: /var/folders/bm/0qdgsxyn1jd2rtcgmvd3jdc80000gn/T/tmpzyid0iq_
    ...the following asset: href: "https://eap.nearspacelabs.net/download/20191122T125836Z_SWIFTERA/Publish_0/20191122T130410Z_640_ST2_POM1_thumb.jpg"
    type: "image/jpeg"
    eo_bands: RGB
    asset_type: THUMBNAIL
    cloud_platform: GCP
    bucket_manager: "Swiftera"
    bucket_region: "us-central1"
    bucket: "swiftera-processed-data"
    object_path: "20191122T125836Z_SWIFTERA/Publish_0/20191122T130410Z_640_ST2_POM1_thumb.jpg"
    
    200 OK
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

