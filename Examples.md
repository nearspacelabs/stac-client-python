# Complex Queries
Below are a few complex queries, downloading and filtering of StacItem results. You can also look through the [test directory](./test) for more examples of how to use queries.

- [Electro Optical](#electro-optical)
- [Limits and Offsets](#limits-and-offsets)

## Electro Optical
Proto3, the version of proto definition used for gRPC STAC, creates messages that are similar to structs in C. One of the drawbacks to structs is that for floats, integers, enums and booleans all fields that are not set are initialized to a value of zero. In geospatial sciences, defaulting to zero can cause problems in that an algorithm or user might interpret that as a true value. 

To get around this, Google uses wrappers for floats and ints and some of those are used in gRPC STAC. For example, some of the fields like `off_nadir`, `azimuth` and others in the Electro Optical protobuf message, [Eo](https://geo-grpc.github.io/api/#epl.protobuf.Eo), use the `google.protobuf.FloatValue` wrapper. As a consequence, accessing those values requires calling `field_name.value` instead of `field_name` to access the data.

For our ground sampling distance query we're using another query filter; this time it's the [FloatField](https://geo-grpc.github.io/api/#epl.protobuf.FloatField). It behaves just as the TimestampField, but with floats for `value` or for `start` + `stop`.

In order to make our off nadir query we need to insert it inside of an [EoRequest](https://geo-grpc.github.io/api/#epl.protobuf.EoRequest) container and set that to the `eo` field of the `StacRequest`.






<details><summary>Expand Python Code Sample</summary>


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




<details><summary>Expand Python Print-out</summary>


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

## Limits and Offsets
It may be that while using the `client.search` request, you've requested so much data that you overrun the 15 second timeout. If that's the case, then you can search for data using `limit` and `offset`.

For most simple requests, a `limit` and `offset` are not necessary. But if you're going through all the data in the archive or if you've constructed a complex request, it may be necessary.





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest
from epl.protobuf.geometry_pb2 import GeometryData, SpatialReferenceData
# Same geometry as above, but a wkt geometry instead of a geojson
travis_wkt = "POLYGON((-97.9736 30.6251, -97.9188 30.6032, -97.9243 30.5703, -97.8695 30.5484, -97.8476 30.4717, -97.7764 30.4279, -97.5793 30.4991, -97.3711 30.4170, -97.4916 30.2089, -97.6505 30.0719, -97.6669 30.0665, -97.7107 30.0226, -98.1708 30.3567, -98.1270 30.4279, -98.0503 30.6251))" 
geometry_data = GeometryData(wkt=travis_wkt, 
                             sr=SpatialReferenceData(wkid=4326))

# get a client interface to the gRPC channel
client = NSLClient()

limit = 200
offset = 0
total = 0
while total < 1000:
    # make our request
    stac_request = StacRequest(geometry=geometry_data, limit=limit, offset=offset)
    # prepare request for next 
    offset += limit
    for stac_item in client.search(stac_request):
        total += 1
        # do cool things with data here
    if total % limit == 0:
        print("stac item id: {0} at {1} index in request".format(stac_item.id, total))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    stac item id: 20191122T130542Z_1701_ST2_POM1 at 200 index in request
    stac item id: 20191122T125916Z_1120_ST2_POM1 at 400 index in request
    stac item id: 20191122T130746Z_504_ST2_POM1 at 600 index in request
    stac item id: 20191122T130858Z_2071_ST2_POM1 at 800 index in request
    stac item id: 20191122T132210Z_1964_ST2_POM1 at 1000 index in request
```


</details>



As you can see in the above results, the `search` request is made 5 different times in the while loop. Each time the `limit` is 200 and the `offset` is increased by 200. 
