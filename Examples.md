# Complex Queries
Below are a few complex queries, downloading and filtering of StacItem results. You can also look through the [test directory](./test) for more examples of how to use queries.

- [Electro Optical](#electro-optical)
- [Sort Order](#sort-order)

### Electro Optical
Proto3, the version of proto definition used for gRPC STAC, creates messages that are similar to structs in C. One of the drawbacks to structs is that for floats, integers, enums and booleans all fields that are not set are initialized to a value of zero. In geospatial sciences, defaulting to zero can cause problems in that an algorithm or user might interpret that as a true value. 

To get around this, Google uses wrappers for floats and ints and some of those are used in gRPC STAC. For example, some of the fields like `off_nadir`, `azimuth` and others in the Electro Optical protobuf message, [Eo](https://geo-grpc.github.io/api/#epl.protobuf.Eo), use the `google.protobuf.FloatValue` wrapper. As a consequence, accessing those values requires calling `field_name.value` instead of `field_name` to access the data.

For our ground sampling distance query we're using another query filter; this time it's the [FloatField](https://geo-grpc.github.io/api/#epl.protobuf.FloatField). It behaves just as the TimestampField, but with floats for `value` or for `start` + `stop`.

In order to make our off nadir query we need to insert it inside of an [EoRequest](https://geo-grpc.github.io/api/#epl.protobuf.EoRequest) container and set that to the `eo` field of the `StacRequest`.






<details><summary>Python Code Sample</summary>


```python
from datetime import datetime, timezone
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.geometry_pb2 import GeometryData, SpatialReferenceData
from epl.protobuf.query_pb2 import FloatField, LT_OR_EQ
from epl.protobuf.stac_pb2 import EoRequest, Eo

# create our ground sampling distance query to only return data less than or equal to 1 meter
off_nadir = FloatField(value=15.0, rel_type=LT_OR_EQ)
# create an eo_request container
eo_request = EoRequest(off_nadir=off_nadir)
# define ourselves a point in Texas
someplace_texas = "POINT(-97.72493696704974 30.25539788861046)"
geometry_data = GeometryData(wkt=someplace_texas, sr=SpatialReferenceData(wkid=4326))
# create a StacRequest with geometry, eo_request and a limit of 20
stac_request = StacRequest(geometry=geometry_data, eo=eo_request, limit=20)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("{0} STAC item '{1}' from {2}\nhas a off_nadir {3:.3f}, which should be less than or "
          "equal to requested off_nadir {4}: confirmed {5}".format(
        Eo.Constellation.Name(stac_item.eo.constellation),
        stac_item.id,
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        stac_item.eo.off_nadir.value,
        off_nadir.value,
        True))
```


</details>




<details><summary>Python Print-out</summary>


```text
    nsl client connecting to stac service at: eap.nearspacelabs.net:9090
    
    SWIFT STAC item '20191122T130514Z_578_ST2_POM1' from 2019-08-22T18:29:40+00:00
    has a off_nadir 13.967, which should be less than or equal to requested off_nadir 15.0: confirmed True
    SWIFT STAC item '20191122T130519Z_578_ST2_POM1' from 2019-08-22T18:29:40+00:00
    has a off_nadir 13.967, which should be less than or equal to requested off_nadir 15.0: confirmed True
```


</details>



Notice that the off_nadir value is printed with some floating point limiting (`:.3f`). Printing out the full value in python would introduce floating point precicion errors for the item. This is because the FloatValue is a float32, but python want's all number to be as large and precise as possible. This is something to be aware of when using Python in general.

Also, even though we set the `limit` to 20, the print out only returns 2 values. For this location, there were only two scenes that were captured with that off nadir angle.


### Sort Order
We can also apply a sort direction to our results so that they are ascending or decending. In the below sample we search all data before 2017 starting with the oldest results first by specifiying the `ASC`, ascending parameter. This is a complex query and can take a while.

**WARNING** this query will take a while.





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

