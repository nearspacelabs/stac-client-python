# Complex Queries
Below are a few complex queries, downloading and filtering of StacItem results. You can also look through the [test directory](./test) for more examples of how to use queries.

- [View Optical](#view)
- [Limits and Offsets](#limits-and-offsets)

## View
Proto3, the version of proto definition used for gRPC STAC, creates messages that are similar to structs in C. One of the drawbacks to structs is that for floats, integers, enums and booleans all fields that are not set are initialized to a value of zero. In geospatial sciences, defaulting to zero can cause problems in that an algorithm or user might interpret that as a true value. 

To get around this, Google uses wrappers for floats and ints and some of those are used in gRPC STAC. For example, some of the fields like `off_nadir`, `azimuth` and others in the View protobuf message, [View](https://geo-grpc.github.io/api/#epl.protobuf.v1.View), use the `google.protobuf.FloatValue` wrapper. As a consequence, accessing those values requires calling `field_name.value` instead of `field_name` to access the data.

For our ground sampling distance query we're using another query filter; this time it's the [FloatFilter](https://geo-grpc.github.io/api/#epl.protobuf.v1.FloatFilter). It behaves just as the TimestampFilter, but with floats for `value` or for `start` + `end`.

In order to make our off nadir query we need to insert it inside of an [ViewRequest](https://geo-grpc.github.io/api/#epl.protobuf.v1.ViewRequest) container and set that to the `view` field of the `StacRequest`.






<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime, timezone
from nsl.stac.client import NSLClient
from nsl.stac import StacRequest, GeometryData, ProjectionData, ViewRequest, View, FloatFilter
from nsl.stac.enum import FilterRelationship, Mission

# create our off_nadir query to only return data captured with an angle of less than or 
# equal to 10 degrees
off_nadir = FloatFilter(value=10.0, rel_type=FilterRelationship.LTE)
# create an eo_request container
view_request = ViewRequest(off_nadir=off_nadir)
# define ourselves a point in Texas
ut_stadium_wkt = "POINT(-97.7323317 30.2830764)"
geometry_data = GeometryData(wkt=ut_stadium_wkt, proj=ProjectionData(epsg=4326))
# create a StacRequest with geometry, eo_request and a limit of 20
stac_request = StacRequest(intersects=geometry_data, view=view_request, limit=20)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("{0} STAC item '{1}' from {2}\nhas a off_nadir {3:.3f}, which should be less than or "
          "equal to requested off_nadir {4}: confirmed {5}".format(
        stac_item.mission,
        stac_item.id,
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        stac_item.view.off_nadir.value,
        off_nadir.value,
        True))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    found NSL_ID <OMITTED> under profile name `default`
    nsl client connecting to stac service at: api.nearspacelabs.net:9090
    
    authorizing NSL_ID: `<OMITTED>`
    attempting NSL authentication against https://api.nearspacelabs.net/oauth/token...
    successfully authenticated with NSL_ID: `<OMITTED>`
    will attempt re-authorization in 60 minutes
    SWIFT STAC item '20200703T174443Z_650_POM1_ST2_P' from 2020-07-03T17:44:43+00:00
    has a off_nadir 1.980, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20200703T174028Z_513_POM1_ST2_P' from 2020-07-03T17:40:28+00:00
    has a off_nadir 9.310, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20200703T174021Z_509_POM1_ST2_P' from 2020-07-03T17:40:21+00:00
    has a off_nadir 8.052, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190822T183518Z_746_POM1_ST2_P' from 2019-08-22T18:35:18+00:00
    has a off_nadir 9.423, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190822T183510Z_742_POM1_ST2_P' from 2019-08-22T18:35:10+00:00
    has a off_nadir 9.349, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190821T180042Z_568_POM1_ST2_P' from 2019-08-21T18:00:42+00:00
    has a off_nadir 9.685, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190821T180028Z_561_POM1_ST2_P' from 2019-08-21T18:00:28+00:00
    has a off_nadir 8.978, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190821T180002Z_548_POM1_ST2_P' from 2019-08-21T18:00:02+00:00
    has a off_nadir 9.282, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190821T175954Z_544_POM1_ST2_P' from 2019-08-21T17:59:54+00:00
    has a off_nadir 8.855, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190821T175943Z_539_POM1_ST2_P' from 2019-08-21T17:59:43+00:00
    has a off_nadir 8.956, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190818T174304Z_205_POM1_ST2_P' from 2019-08-18T17:43:04+00:00
    has a off_nadir 7.015, which should be less than or equal to requested off_nadir 10.0: confirmed True
    SWIFT STAC item '20190818T174227Z_181_POM1_ST2_P' from 2019-08-18T17:42:27+00:00
    has a off_nadir 8.237, which should be less than or equal to requested off_nadir 10.0: confirmed True
```


</details>



Notice that the off_nadir value is printed with some floating point limiting (`:.3f`). Printing out the full value in python would introduce floating point precicion errors for the item. This is because the FloatValue is a float32, but python want's all number to be as large and precise as possible. This is something to be aware of when using Python in general.

Also, even though we set the `limit` to 20, the print out only returns 2 values. For this location, there were only two scenes that were captured with that off nadir angle.

## Limits and Offsets
It may be that while using the `client.search` request, you've requested so much data that you overrun the 15 second timeout. If that's the case, then you can search for data using `limit` and `offset`.

For most simple requests, a `limit` and `offset` are not necessary. But if you're going through all the data in the archive or if you've constructed a complex request, it may be necessary.





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import date
from nsl.stac.client import NSLClient
from nsl.stac import StacRequest, GeometryData, ProjectionData, enum
from nsl.stac.utils import pb_timestampfield
# wkt geometry of Travis County, Texas
travis_wkt = "POLYGON((-97.9736 30.6251, -97.9188 30.6032, -97.9243 30.5703, \
                -97.8695 30.5484, -97.8476 30.4717, -97.7764 30.4279, \
                -97.5793 30.4991, -97.3711 30.4170, -97.4916 30.2089, \
                -97.6505 30.0719, -97.6669 30.0665, -97.7107 30.0226, \
                -98.1708 30.3567, -98.1270 30.4279, -98.0503 30.6251))" 

# Query data from before September 1, 2019
time_filter = pb_timestampfield(value=date(2019, 9, 1), rel_type=enum.FilterRelationship.LTE)

geometry_data = GeometryData(wkt=travis_wkt, 
                             proj=ProjectionData(epsg=4326))

# get a client interface to the gRPC channel
client = NSLClient()

limit = 200
offset = 0
total = 0
while total < 1000:
    # make our request
    stac_request = StacRequest(datetime=time_filter, intersects=geometry_data, limit=limit, offset=offset)
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
    stac item id: 20190829T172909Z_1600_POM1_ST2_P at 200 index in request
    stac item id: 20190829T172054Z_1354_POM1_ST2_P at 400 index in request
    stac item id: 20190829T171353Z_1152_POM1_ST2_P at 600 index in request
    stac item id: 20190829T170044Z_770_POM1_ST2_P at 800 index in request
    stac item id: 20190829T165121Z_495_POM1_ST2_P at 1000 index in request
```


</details>



As you can see in the above results, the `search` request is made 5 different times in the while loop. Each time the `limit` is 200 and the `offset` is increased by 200. 
