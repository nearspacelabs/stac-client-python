# Experimental Features
Here are some examples of experimental features we're planning to add to our API. These wrappers abstract away some
parts of the protobuf structs, and provide easier access to geometries and `datetime`.

## First Code Example
This is an alternative to the original version [here](./README.md#first-code-example). This simplifies the setting of
the `observed` field and hides the use of more verbose protobuf classes for both time filter (`observed`) and spatial
filter (`intersects`).





<details><summary>Expand Python Code Sample</summary>


```python
import tempfile
from datetime import date

from shapely.wkt import loads as load_wkt_shapely

from IPython.display import Image, display
from epl.geometry import Point
from nsl.stac import enum, utils
from nsl.stac.experimental import NSLClientEx, StacRequestWrap

# the client package stubs out a little bit of the gRPC connection code 
# get a client interface to the gRPC channel. This client singleton is threadsafe
client = NSLClientEx()

# create our request. this interface allows us to set fields in our protobuf object
request = StacRequestWrap()

# our area of interest will be the coordinates of the UT Stadium in Austin Texas
# the order of coordinates here is longitude then latitude (x, y). The results of our query 
# will be returned only if they intersect this point geometry we've defined (other geometry 
# types besides points are supported)
#
# This string format, POINT(float, float) is the well-known-text geometry format:
# https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
#
# the epsg # defines the WGS-84 elispsoid (`epsg=4326`) spatial reference 
# (the latitude longitude  spatial reference most commonly used)
#
# the epl.geometry Point class is an extension of shapely's Point class that supports
# the protobuf definitions we use with STAC. To extract a shapely geometry from it use
# the shapely_dump property
request.intersects = Point.import_wkt(wkt="POINT(-97.7323317 30.2830764)", epsg=4326)
# or using `shapely`
request.intersects = load_wkt_shapely("POINT(-97.7323317 30.2830764)")

# The `set_observed` method allows for making sql-like queries on the observed field and the
# LTE is an enum that means less than or equal to the value in the query field
#
# This Query is for data from August 25, 2019 UTC or earlier
request.set_observed(rel_type=enum.FilterRelationship.LTE, value=date(2019, 8, 25))

# search_one_ex method requests only one item be returned that meets the query filters in the StacRequestWrap
# the item returned is a wrapper of the protobuf message; StacItemWrap. search_one_ex, will only return the most
# recently observed results that matches the time filter and spatial filter
stac_item = client.search_one_ex(request)

# get the thumbnail asset from the assets map. The other option would be a Geotiff, 
# with asset key 'GEOTIFF_RGB'
asset_wrap = stac_item.get_asset(asset_type=enum.AssetType.THUMBNAIL)

print(asset_wrap)
# uncomment to display image
# with tempfile.TemporaryDirectory() as d:
#     filename = utils.download_asset(asset=asset, save_directory=d)
#     display(Image(filename=filename))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    found NSL_ID <OMITTED> under profile name `default`
    nsl client connecting to stac service at: api.nearspacelabs.net:9090
    
    warning, no projection data set. assuming WGS84
    authorizing NSL_ID: `<OMITTED>`
    attempting NSL authentication against https://api.nearspacelabs.net/oauth/token...
    successfully authenticated with NSL_ID: `<OMITTED>`
    will attempt re-authorization in 60 minutes
    href: "https://api.nearspacelabs.net/download/20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.png"
    type: "image/png"
    eo_bands: RGB
    asset_type: THUMBNAIL
    cloud_platform: GCP
    bucket_manager: "Near Space Labs"
    bucket_region: "us-central1"
    bucket: "swiftera-processed-data"
    object_path: "20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.png"
    extension: .png
    asset_key: THUMBNAIL_RGB
```


</details>



## Simple Query and the Makeup of a StacItem
The easiest query to construct is a `StacRequestWrap` constructor with no variables, and the next simplest, is the case
where we know the STAC item `id` that we want to search. If we already know the STAC `id` of an item, we can construct
the `StacRequestWrap` as follows:





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.experimental import NSLClientEx, StacRequestWrap

# get a client interface to the gRPC channel
client_ex = NSLClientEx()

# create a request for a specific STAC item
request = StacRequestWrap(id='20190822T183518Z_746_POM1_ST2_P')

# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one_ex(request)
print(stac_item)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    id: "20190822T183518Z_746_POM1_ST2_P"
    collection: "NSL_SCENE"
    properties {
      type_url: "nearspacelabs.com/proto/st.protobuf.v1.NslDatast.protobuf.v1.NslData/st.protobuf.v1.NslData"
      value: "\n\340\014\n\03620190822T162258Z_TRAVIS_COUNTY\"\003 \352\0052\03520200702T102306Z_746_ST2_POM1:\03520190822T183518Z_746_POM1_ST2:\03520200702T101632Z_746_ST2_POM1:\03520200702T102302Z_746_ST2_POM1:\03520200702T102306Z_746_ST2_POM1B\03520190822T183518Z_746_POM1_ST2H\001R\374\n\n$\004\304{?\216\371\350=\376\377\306>\300\327\256\275\323rv?2\026*D3Qy6\177>\3675\000\000\200?\022\024\r+}\303\302\025\033;\362A\0353}\367\300%g\232\250@\022\024\r\026}\303\302\025\376?\362A\035\000\367\235@%\232\t\331?\022\024\r\351|\303\302\025\021A\362A\035M\370\033\301%g\016\226\277\022\024\r\201|\303\302\025\3709\362A\035\000\252\245@%\315\3547?\022\024\r\310|\303\302\025\245G\362A\035\232\315l\301%3\347\270\300\022\024\rq|\303\302\025\2149\362A\035\000\376o@%\000(\017@\022\024\rD|\303\302\025oD\362A\0353\323\302\301%\315\306\230\300\022\024\r\031|\303\302\025\035=\362A\035g\277$A%\000\340\231?\022\024\rE|\303\302\025\215I\362A\0353\275z\300%g\020\236\300\022\024\r\345{\303\302\0258C\362A\035\0008\242?%\232\231\226\277\022\024\r\010|\303\302\025!I\362A\0353\377\212\300%\000V\241\300\022\024\r|{\303\302\025\207F\362A\0353\203Y@%\315,\313\276\022\024\r\001{\303\302\025FJ\362A\035g^\025@%\315\010\214?\022\024\r\313z\303\302\025\353H\362A\0353\3377@%g\326\325\277\022\024\rjz\303\302\025\260@\362A\035\315F\006A%g\246[\277\022\024\r\035z\303\302\0254E\362A\035\232\001|@%\232!\265?\022\024\r\330y\303\302\025\320@\362A\0353Sa\300%\000@\245>\022\024\r\362y\303\302\025zE\362A\035\232\221\020\300%3U\206@\022\024\r\337y\303\302\025\210F\362A\035g\246l?%gf\234\276\022\024\r\335y\303\302\025aF\362A\035\000\260\023@%\315,#\277\022\024\r\321y\303\302\025\234F\362A\035\000 7@%\232!\221?\022\024\r\307y\303\302\025\177F\362A\035\232\371\371?%\315\224\225?\022\024\r\213y\303\302\025\350@\362A\0353\'\343\300%3g&\300\022\024\r\300y\303\302\025\tF\362A\035\315h\312@%g\266\013?\022\024\r_y\303\302\025\236A\362A\035\315\340\311@%3\363j>\022\024\r\271x\303\302\025G?\362A\0353\334\272\301%gb\201\300\022\024\r\307x\303\302\025WG\362A\035\000|6\301%\232\231i>\022\024\r\200x\303\302\025\016F\362A\035\315\007\244\301%\315L\000>\022\024\rqx\303\302\025jI\362A\035\315\254\007\301%\232E\247?\022\024\rjx\303\302\025(I\362A\035\232\305\000\301%\315L\'>\022\024\r\027x\303\302\025\356A\362A\035\232I\246?%\315\004\246\277\022\024\r\010x\303\302\025AB\362A\035\232y\305\300%\315\3740?\022\024\r\032x\303\302\0257D\362A\0353\003\275\277%\232\311.?\022\024\r\002x\303\302\025&C\362A\035\315\014\301\277%g*2@\022\024\r\361w\303\302\025\330B\362A\035\000T\347\300%\232\235\025\300\022\024\r\372v\303\302\025\030<\362A\0353\323\364?%gNt\300\022\024\r;w\303\302\025\273I\362A\03533\335>%\232\025\213?\022\024\r\324v\303\302\025QC\362A\035\315,\305\277%\232\375\035@\022\024\r\340v\303\302\025@G\362A\035\315@\234\300%\232)\342?\022\024\r\312v\303\302\025yC\362A\035\315\214\247\276%g\246\375>\022\024\r\222v\303\302\025\233A\362A\035\315\334\244?%g\366\035\277\022\024\r\256v\303\302\025\\F\362A\0353G\204@%\232A\017@\022\024\rov\303\302\025\215=\362A\035\232\325\340@%3\263\033\276\022\024\r\206v\303\302\025SC\362A\0353\263k?%3\363\177\276\022\024\r\267v\303\302\025NK\362A\035\315\0148\277%3\323\000>\022\024\r\255v\303\302\025kK\362A\035gf4\277%\000\312\201\277\022\024\r)v\303\302\025\316=\362A\035\232\271Z\277%\315\014\375\277\022\024\r_v\303\302\025\356H\362A\035\315\004n@%3\243\240\276\022\024\r7v\303\302\025\350H\362A\0353#\212@%g~\272?\022\024\r\314u\303\302\025Y;\362A\035\000\000F=%gF\253?\022\024\r\276u\303\302\025q>\362A\0353/\234\300%g\246T\277\022\024\r\266u\303\302\025\321>\362A\035\315 \272\300%3SW\300\022\024\r\307u\303\302\025\211A\362A\035\000$\264\300%3\243\r\277\022\024\r\360u\303\302\025RK\362A\0353\347\231@%\315\325\036\300\022\024\r\262u\303\302\025\035F\362A\0353\2633\276%\232i3?\032#m_3009743_sw_14_1_20160928_20161129\"Y\t&\2068NM\357\"A\021\003\3272rL\217IA\031\267G\014x\260\375\"A!\202I\225>\020\222IA*3\0221+proj=utm +zone=14 +datum=NAD83 +units=m +no_defs*\005\r\205[\"A2\005\r\000\356\\@:\005\r\227\210\306AB\005\r\205E\257@\022\315\001\n e502fe83507f0d28c826f33619a678e9\022\03120200806T033934Z_SWIFTERA\030\010 \377\377\377\377\377\377\377\377\377\001(A0\0018\340\025@\330\247\004H\270\275\004R\03620190822T162258Z_TRAVIS_COUNTYR\03120200701T112634Z_SWIFTERAR\03120200701T112634Z_SWIFTERAR\03120200701T112634Z_SWIFTERAX\263\027"
    }
    assets {
      key: "GEOTIFF_RGB"
      value {
        href: "https://api.nearspacelabs.net/download/20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.tif"
        type: "image/vnd.stac.geotiff"
        eo_bands: RGB
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Near Space Labs"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.tif"
      }
    }
    assets {
      key: "THUMBNAIL_RGB"
      value {
        href: "https://api.nearspacelabs.net/download/20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.png"
        type: "image/png"
        eo_bands: RGB
        asset_type: THUMBNAIL
        cloud_platform: GCP
        bucket_manager: "Near Space Labs"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.png"
      }
    }
    geometry {
      wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\352\244L\267\311oX\300\316\340\320\247\234I>@\241\273\2606\267oX\300<\002\205\'EG>@\031\003\203\307\266nX\3001z\244\372\233G>@CCAI\306nX\300\326\013\351\023\343I>@\352\244L\267\311oX\300\316\340\320\247\234I>@"
      proj {
        epsg: 4326
      }
      envelope {
        xmin: -97.7466867683867
        ymin: 30.278398961994966
        xmax: -97.72990596574927
        ymax: 30.288621181865743
        proj {
          epsg: 4326
        }
      }
      simple: STRONG_SIMPLE
    }
    bbox {
      xmin: -97.7466867683867
      ymin: 30.278398961994966
      xmax: -97.72990596574927
      ymax: 30.288621181865743
      proj {
        epsg: 4326
      }
    }
    datetime {
      seconds: 1566498918
      nanos: 505476000
    }
    observed {
      seconds: 1566498918
      nanos: 505476000
    }
    created {
      seconds: 1596743811
      nanos: 247169000
    }
    updated {
      seconds: 1612193286
      nanos: 12850810
    }
    platform_enum: SWIFT_2
    platform: "SWIFT_2"
    instrument_enum: POM_1
    instrument: "POM_1"
    constellation: "UNKNOWN_CONSTELLATION"
    mission_enum: SWIFT
    mission: "SWIFT"
    gsd {
      value: 0.20000000298023224
    }
    eo {
    }
    view {
      off_nadir {
        value: 9.42326831817627
      }
      azimuth {
        value: -74.85270690917969
      }
      sun_azimuth {
        value: 181.26959228515625
      }
      sun_elevation {
        value: 71.41288757324219
      }
    }
    
```


</details>



## Spatial Queries

### Query by Bounds
You can query for STAC items intersecting a bounding box of minx, miny, maxx, and maxy. An
[epsg](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset) code is required (4326 is the most common epsg
code used for longitude and latitude). Remember, this finds STAC items that intersect the bounds, **not** STAC items
contained by the bounds.





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.experimental import StacRequestWrap, NSLClientEx

# get a client interface to the gRPC channel
client_ex = NSLClientEx()

# request wrapper
request = StacRequestWrap()

# define our area of interest bounds using the xmin, ymin, xmax, ymax coordinates of an area on 
# the WGS-84 ellipsoid
neighborhood_box = (-97.7352547645, 30.27526474757116, -97.7195692, 30.28532)
# setting the bounds tests for intersection (not contains)
request.set_bounds(neighborhood_box, epsg=4326)
request.limit = 3

# Search for data that intersects the bounding box
epsg_4326_ids = []
for stac_item in client_ex.search_ex(request):
    print("STAC item id: {}".format(stac_item.id))
    print("bounds:")
    print(stac_item.geometry.bounds)
    print("bbox (EnvelopeData protobuf):")
    print(stac_item.bbox)
    print("geometry:")
    print(stac_item.geometry)
    epsg_4326_ids.append(stac_item.id)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20220129T180742Z_2109_POM1_ST3_16_P
    bounds:
    (-97.7243210583828, 30.27549788764243, -97.7185223808856, 30.279102560831348)
    bbox (EnvelopeData protobuf):
    xmin: -97.7243210583828
    ymin: 30.27549788764243
    xmax: -97.7185223808856
    ymax: 30.279102560831348
    proj {
      epsg: 4326
    }
    
    geometry:
    MULTIPOLYGON (((-97.72430785966142 30.27910256083135, -97.7243210583828 30.27564945279034, -97.7185357817901 30.27549788764243, -97.7185223808856 30.27895098917852, -97.72430785966142 30.27910256083135)))
    STAC item id: 20220129T180729Z_2099_POM1_ST3_16_P
    bounds:
    (-97.72820238756172, 30.273151146802945, -97.7224676466358, 30.276666327832757)
    bbox (EnvelopeData protobuf):
    xmin: -97.72820238756172
    ymin: 30.273151146802945
    xmax: -97.7224676466358
    ymax: 30.276666327832757
    proj {
      epsg: 4326
    }
    
    geometry:
    MULTIPOLYGON (((-97.72820238756172 30.27666632783276, -97.72819485907814 30.27327542943616, -97.72246764663581 30.27315114680295, -97.72247497830368 30.27654204009979, -97.72820238756172 30.27666632783276)))
    STAC item id: 20220129T180725Z_2096_POM1_ST3_16_P
    bounds:
    (-97.72821731889985, 30.27535948360813, -97.72239956629605, 30.2789016672645)
    bbox (EnvelopeData protobuf):
    xmin: -97.72821731889985
    ymin: 30.27535948360813
    xmax: -97.72239956629605
    ymax: 30.2789016672645
    proj {
      epsg: 4326
    }
    
    geometry:
    MULTIPOLYGON (((-97.72821731889985 30.2789016672645, -97.72818578293491 30.2754806908654, -97.72239956629605 30.27535948360813, -97.72243090118636 30.27878045536211, -97.72821731889985 30.2789016672645)))
```


</details>



### Query by Bounds; Projection Support
Querying using geometries defined in a different projection requires defining the epsg number for the spatial reference
of the data. In this example we use an epsg code for a [UTM projection](https://epsg.io/3744).

Notice that the results below are the same as the cell above (look at the `TEST-->` section of the printout)





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.experimental import StacRequestWrap, NSLClientEx

# get a client interface to the gRPC channel
client_ex = NSLClientEx()

# request wrapper
request = StacRequestWrap()

# define our area of interest bounds using the xmin, ymin, xmax, ymax coordinates of in UTM 14N in NAD83 (epsg 3744)
neighborhood_box = (621636.1875228449, 3349964.520449501, 623157.4212553708, 3351095.8075163467)
# setting the bounds tests for contains query
request.set_bounds(neighborhood_box, epsg=3744)
request.limit = 3

# Search for data that intersects the bounding box
for stac_item in client_ex.search_ex(request):
    print("STAC item id: {}".format(stac_item.id))
    print("bounds:")
    print(stac_item.geometry.bounds)
    print("bbox (EnvelopeData protobuf):")
    print(stac_item.bbox)
    print("geometry:")
    print(stac_item.geometry)
    print("TEST RESULT '{1}': stac_item id {0} from 3744 bounds is in the set of the 4326 bounds search results."
          .format(stac_item.id, stac_item.id in epsg_4326_ids))
    print()


```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20220129T180742Z_2109_POM1_ST3_16_P
    bounds:
    (-97.7243210583828, 30.27549788764243, -97.7185223808856, 30.279102560831348)
    bbox (EnvelopeData protobuf):
    xmin: -97.7243210583828
    ymin: 30.27549788764243
    xmax: -97.7185223808856
    ymax: 30.279102560831348
    proj {
      epsg: 4326
    }
    
    geometry:
    MULTIPOLYGON (((-97.72430785966142 30.27910256083135, -97.7243210583828 30.27564945279034, -97.7185357817901 30.27549788764243, -97.7185223808856 30.27895098917852, -97.72430785966142 30.27910256083135)))
    TEST RESULT 'True': stac_item id 20220129T180742Z_2109_POM1_ST3_16_P from 3744 bounds is in the set of the 4326 bounds search results.
    
    STAC item id: 20220129T180729Z_2099_POM1_ST3_16_P
    bounds:
    (-97.72820238756172, 30.273151146802945, -97.7224676466358, 30.276666327832757)
    bbox (EnvelopeData protobuf):
    xmin: -97.72820238756172
    ymin: 30.273151146802945
    xmax: -97.7224676466358
    ymax: 30.276666327832757
    proj {
      epsg: 4326
    }
    
    geometry:
    MULTIPOLYGON (((-97.72820238756172 30.27666632783276, -97.72819485907814 30.27327542943616, -97.72246764663581 30.27315114680295, -97.72247497830368 30.27654204009979, -97.72820238756172 30.27666632783276)))
    TEST RESULT 'True': stac_item id 20220129T180729Z_2099_POM1_ST3_16_P from 3744 bounds is in the set of the 4326 bounds search results.
    
    STAC item id: 20220129T180725Z_2096_POM1_ST3_16_P
    bounds:
    (-97.72821731889985, 30.27535948360813, -97.72239956629605, 30.2789016672645)
    bbox (EnvelopeData protobuf):
    xmin: -97.72821731889985
    ymin: 30.27535948360813
    xmax: -97.72239956629605
    ymax: 30.2789016672645
    proj {
      epsg: 4326
    }
    
    geometry:
    MULTIPOLYGON (((-97.72821731889985 30.2789016672645, -97.72818578293491 30.2754806908654, -97.72239956629605 30.27535948360813, -97.72243090118636 30.27878045536211, -97.72821731889985 30.2789016672645)))
    TEST RESULT 'True': stac_item id 20220129T180725Z_2096_POM1_ST3_16_P from 3744 bounds is in the set of the 4326 bounds search results.
    
```


</details>



### Query by GeoJSON
Use a GeoJSON geometry to define the `intersects` property.





<details><summary>Expand Python Code Sample</summary>


```python
import json
import requests
from epl.geometry import shape as epl_shape

from nsl.stac.experimental import StacRequestWrap, NSLClientEx

# get a client interface to the gRPC channel
client_ex = NSLClientEx()

request = StacRequestWrap()

# retrieve a coarse geojson foot print of Travis County, Texas
r = requests.get("http://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/TX/Travis.geo.json")
travis_shape = epl_shape(r.json()['features'][0]['geometry'], epsg=4326)

# search for any data that intersects the travis county geometry
request.intersects = travis_shape

# limit results to 2 (instead of default of 10)
request.limit = 2

geojson_ids = []
# get a client interface to the gRPC channel
for stac_item in client_ex.search_ex(request):
    print("STAC item id: {}".format(stac_item.id))
    print("Stac item observed: {}".format(stac_item.observed))
    geojson_ids.append(stac_item.id)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20220130T191536Z_1489_POM1_ST3_26_P
    Stac item observed: 2022-01-30 19:15:36+00:00
    STAC item id: 20220130T191127Z_1425_POM1_ST3_26_P
    Stac item observed: 2022-01-30 19:11:27+00:00
```


</details>



### Query by WKT
Use a [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) geometry to define the
`intersects` property.





<details><summary>Expand Python Code Sample</summary>


```python
from epl.geometry import Polygon

# Same geometry as above, but a wkt geometry instead of a geojson
travis_wkt = "POLYGON((-97.9736 30.6251, -97.9188 30.6032, -97.9243 30.5703, -97.8695 30.5484, \
              -97.8476 30.4717, -97.7764 30.4279, -97.5793 30.4991, -97.3711 30.4170, \
              -97.4916 30.2089, -97.6505 30.0719, -97.6669 30.0665, -97.7107 30.0226, \
              -98.1708 30.3567, -98.1270 30.4279, -98.0503 30.6251, -97.9736 30.6251))" 
request.intersects = Polygon.import_wkt(wkt=travis_wkt, epsg=4326)
request.limit = 2
for stac_item in client_ex.search_ex(request):
    print("STAC item id: {0} from wkt filter intersects result from geojson filter: {1}"
          .format(stac_item.id, stac_item.id in geojson_ids))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20220130T191536Z_1489_POM1_ST3_26_P from wkt filter intersects result from geojson filter: True
    STAC item id: 20220130T191127Z_1425_POM1_ST3_26_P from wkt filter intersects result from geojson filter: True
```


</details>



## Temporal Queries
When it comes to Temporal queries there are a few things to note. 

- we assume all dates are UTC unless specified
- datetime and date are treated differently in different situations
  - date for EQ and NEQ is a 24 hour period
  - datetime for EQ and NEQ is almost useless (it is a timestamp accurate down to the nanosecond)
  - date for GTE or LT is defined as the date from the first nanosecond of that date
  - date for LTE or GT is defined as the date at the final nanosecond of that date
  - date for start and end with BETWEEN has a start with minimum time and an end with the max time. same for NOT_BETWEEN
  - datetime for GTE, GT, LTE, LT, BETWEEN and NOT_BETWEEN is interpreted strictly according to the nanosecond of that
  datetime definition(s) provided

When creating a time query filter, we want to use the >, >=, <, <=, ==, != operations and inclusive and exclusive range
requests. We do this by using the `set_observed` method and the `value` set to a date/datetime combined with `rel_typ`
set to `GTE`,`GT`, `LTE`, `LT`, `EQ`, or `NEQ`. If we use `rel_type` set to `BETWEEN` OR `NOT_BETWEEN` then we must set
the `start` **and** the `end` variables.

### Everything After A Specific Date





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import date, datetime
from nsl.stac.experimental import NSLClientEx, StacRequestWrap
from nsl.stac import enum

# get a client interface to the gRPC channel
client_ex = NSLClientEx()

request = StacRequestWrap()

# make a filter that selects all data on or after August 21st, 2019
request.set_observed(rel_type=enum.FilterRelationship.GTE, value=date(2019, 8, 21))
request.limit = 2

demonstration_datetime = datetime.combine(date(2019, 8, 21), datetime.min.time())

for stac_item in client_ex.search_ex(request):
    print("STAC item date, {0}, is after {1}: {2}".format(
        stac_item.observed,
        demonstration_datetime,
        datetime.timestamp(stac_item.observed) > datetime.timestamp(demonstration_datetime)))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item date, 2022-02-08 17:02:32+00:00, is after 2019-08-21 00:00:00: True
    STAC item date, 2022-02-08 17:02:30+00:00, is after 2019-08-21 00:00:00: True
```


</details>



#### Everything Between Two Dates

Now we're going to do a range request and select data between two dates using the `start` and `end` parameters instead
of the `value` parameter:





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime, timezone, timedelta
from nsl.stac import enum

# Query data from August 1, 2019
start = datetime(2019, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
# ... up until August 10, 2019
end = start + timedelta(days=9)

request.set_observed(rel_type=enum.FilterRelationship.BETWEEN, start=start, end=end)
request.limit = 2

# get a client interface to the gRPC channel
client_ex = NSLClientEx()

for stac_item in client_ex.search_ex(request):
    print("STAC item date, {0}, is between {1} and {2}".format(
        stac_item.observed,
        datetime.combine(start, datetime.min.time()),
        datetime.combine(end, datetime.min.time())))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item date, 2019-08-06 20:42:53+00:00, is between 2019-08-01 00:00:00 and 2019-08-10 00:00:00
    STAC item date, 2019-08-06 20:42:51+00:00, is between 2019-08-01 00:00:00 and 2019-08-10 00:00:00
```


</details>



In the above print out we are returned STAC items that are between the dates of Aug 1 2019 and Aug 10 2019. Also, notice
there's no warnings as we defined our utc timezone on the datetime objects.

#### Select Data for One Day

Now we'll search for everything on a specific day using a python `datetime.date` for the `value` and `rel_type` set to
use equals (`FilterRelationship.EQ`). Python's `datetime.datetime` is a specific value and if you use it combined with
`EQ` the query would insist that the time relationship match down to the second. But since `datetime.date` is only
specific down to the day, the filter is created for the entire day. This will check for everything from the start until
the end of the 8th of August, specifically in the Austin, Texas timezone (UTC -6).





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime, timezone, timedelta, date
from nsl.stac.experimental import NSLClientEx, StacItemWrap
from nsl.stac import utils, enum

request = StacRequestWrap()

# Query all data for the entire day of August 6, 2019 (in TX time)
texas_utc_offset = timezone(timedelta(hours=-6))
request.set_observed(value=date(2019, 8, 6), rel_type=enum.FilterRelationship.EQ, tzinfo=texas_utc_offset)

request.limit = 2

# get a client interface to the gRPC channel
client_ex = NSLClientEx()
for stac_item in client_ex.search_ex(request):
    print(datetime.fromtimestamp(stac_item.observed.timestamp(), tz=timezone.utc))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    2019-08-06 20:42:53+00:00
    2019-08-06 20:42:51+00:00
```


</details>



## Query by GSD (ground sampling distance)

Our sample imagery contains both 30cm (0.15-0.20m gsd) and 10cm (0.05m gsd) scenes. Here is a snippet below detailing how to
filter by GSD.





<details><summary>Expand Python Code Sample</summary>


```python
from itertools import islice

from nsl.stac.experimental import NSLClientEx
from nsl.stac import enum

request = StacRequestWrap()

# Query for all imagery whose GSD is less than 0.051 (to account for minor floating point variations)
request.set_gsd(rel_type=enum.FilterRelationship.LTE, value=0.051)

# Restrict search to areas of publicly available 10cm imagery in Austin, TX
request.intersects = Polygon.import_wkt(epsg=4326, wkt='POLYGON((-97.7344436645508 30.326004681223694,'
                                                       '-97.7344436645508 30.29517998555933,'
                                                       '-97.73650360107423 30.28569351372147,'
                                                       '-97.73616027832033 30.273834133861683,'
                                                       '-97.71796417236328 30.274130635825372,'
                                                       '-97.71796417236328 30.28539704669346,'
                                                       '-97.68397521972658 30.293994226755345,'
                                                       '-97.68466186523439 30.32630102546601,'
                                                       '-97.7344436645508 30.326004681223694))')

client_ex = NSLClientEx()

# filter results by the first we can download with basic credentials
items = islice(filter(lambda item: 'REGION_0' in item.get_asset(asset_type=enum.AssetType.GEOTIFF).href,
                      client_ex.search_ex(request, auto_paginate=True)), 1)

stac_item = next(items)
print(stac_item.id)
print(stac_item.gsd)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    20211221T171926Z_855_POM1_ST3_16_P
    0.05000000074505806
```


</details>



## Downloading from AssetWrap





<details><summary>Expand Python Code Sample</summary>


```python
import os
import tempfile
from IPython.display import Image, display

from epl.geometry import LineString
from nsl.stac.experimental import NSLClientEx, StacRequestWrap
from nsl.stac import utils, enum

request = StacRequestWrap()
request.intersects = LineString.import_wkt(wkt='LINESTRING(622301.8284206488 3350344.236542711,'
                                               '622973.3950196661 3350466.792693002)',
                                           epsg=3744)
request.set_observed(value=date(2019, 8, 25), rel_type=enum.FilterRelationship.LTE)
request.limit = 3

client_ex = NSLClientEx()

stac_item = client_ex.search_one_ex(request)
# get the thumbnail asset from the assets map
asset_wrap = stac_item.get_asset(asset_type=enum.AssetType.THUMBNAIL)
print(asset_wrap)

# (side-note delete=False in NamedTemporaryFile is only required for windows.)
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as file_obj:
    asset_wrap.download(file_obj=file_obj)
    print("downloaded file {}".format(os.path.basename(asset_wrap.object_path)))
    print()
    # uncomment to display            
    # display(Image(filename=file_obj.name))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    href: "https://api.nearspacelabs.net/download/20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183418Z_716_POM1_ST2_P.png"
    type: "image/png"
    eo_bands: RGB
    asset_type: THUMBNAIL
    cloud_platform: GCP
    bucket_manager: "Near Space Labs"
    bucket_region: "us-central1"
    bucket: "swiftera-processed-data"
    object_path: "20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183418Z_716_POM1_ST2_P.png"
    extension: .png
    asset_key: THUMBNAIL_RGB
    downloaded file 20190822T183418Z_716_POM1_ST2_P.png
    
```


</details>



## View
For our ground sampling distance query we're using another query filter; this time it's the
[FloatFilter](https://geo-grpc.github.io/api/#epl.protobuf.v1.FloatFilter). It behaves just as the TimestampFilter, but
with floats for `value` or for `start` + `end`.

In order to make our off nadir query we need to insert it inside of an
[ViewRequest](https://geo-grpc.github.io/api/#epl.protobuf.v1.ViewRequest) container and set that to the `view` field of
the `StacRequest`.





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime, timezone
from epl.geometry import Point
from nsl.stac.experimental import NSLClientEx, StacRequestWrap
from nsl.stac.enum import FilterRelationship, Mission

request = StacRequestWrap()

# create our off_nadir query to only return data captured with an angle of less than or 
# equal to 10 degrees
request.set_off_nadir(rel_type=FilterRelationship.GTE, value=30.0)

request.set_gsd(rel_type=FilterRelationship.LT, value=1.0)

# define ourselves a point in Texas
request.intersects = Point.import_wkt("POINT(621920.1090935947 3350833.389847579)", epsg=26914)
# the above could also be defined using longitude and latitude as follows:
# request.intersects = Point.import_wkt("POINT(-97.7323317 30.2830764)", epsg=4326)

# create a StacRequest with geometry, gsd, and off nadir and a limit of 4
request.limit = 4

# get a client interface to the gRPC channel
client_ex = NSLClientEx()
for stac_item in client_ex.search_ex(request):
    print("{0} STAC item '{1}' from {2}\nhas a off_nadir\t{3:.2f}, which should be greater than or "
          "equal to requested off_nadir\t{4:.3f} (confirmed {5})".format(
        stac_item.mission.name,
        stac_item.id,
        stac_item.observed,
        stac_item.off_nadir,
        request.stac_request.view.off_nadir.value,
        request.stac_request.view.off_nadir.value < stac_item.off_nadir))
    print("has a gsd\t{0:.3f}, which should be less than "
          "the requested\t\t  gsd\t\t{1:.3f} (confirmed {2})".format(
        stac_item.gsd,              
        request.stac_request.gsd.value,
        request.stac_request.gsd.value < stac_item.gsd))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    SWIFT STAC item '20211212T173532Z_2006_POM1_ST2_13_P' from 2021-12-12 17:35:32+00:00
```


</details>

    has a off_nadir	30.19, which should be greater than or equal to requested off_nadir	30.000 (confirmed True)
    has a gsd	0.050, which should be less than the requested		  gsd		1.000 (confirmed False)
    SWIFT STAC item '20211212T173531Z_2005_POM1_ST2_13_P' from 2021-12-12 17:35:31+00:00
    has a off_nadir	30.27, which should be greater than or equal to requested off_nadir	30.000 (confirmed True)
    has a gsd	0.050, which should be less than the requested		  gsd		1.000 (confirmed False)
    SWIFT STAC item '20211212T173529Z_2004_POM1_ST2_13_P' from 2021-12-12 17:35:29+00:00
    has a off_nadir	30.33, which should be greater than or equal to requested off_nadir	30.000 (confirmed True)
    has a gsd	0.050, which should be less than the requested		  gsd		1.000 (confirmed False)
    SWIFT STAC item '20211212T173528Z_2003_POM1_ST2_13_P' from 2021-12-12 17:35:28+00:00
    has a off_nadir	30.40, which should be greater than or equal to requested off_nadir	30.000 (confirmed True)
    has a gsd	0.050, which should be less than the requested		  gsd		1.000 (confirmed False)


## Shapely Geometry

Both `StacItemWrap` and `StacRequestWrap` support `shapely` geometries by default, and can be used in place of
`epl.geometry` types.





<details><summary>Expand Python Code Sample</summary>


```python
from shapely.wkt import loads as loads_wkt

from nsl.stac.experimental import NSLClientEx, StacRequestWrap
from nsl.stac import utils, enum

request = StacRequestWrap()

request.intersects = loads_wkt('LINESTRING(-97.72842049283962 30.278624772098176,'
                               '-97.72142529172878 30.2796624743974)')

request.set_observed(value=date(2019, 8, 20), rel_type=enum.FilterRelationship.LTE)
request.limit = 10

client_ex = NSLClientEx()

unioned = None
for stac_item in client_ex.search_ex(request):
    if unioned is None:
        unioned = stac_item.geometry
    else:
        # execute shapely union
        unioned = unioned.union(stac_item.geometry)

print(unioned)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    warning, no projection data set. assuming WGS84
    POLYGON ((-97.72197853142319 30.27298342950026, -97.72178036133324 30.27245385797281, -97.73579589062696 30.26793906410984, -97.73794706841718 30.2741425833901, -97.74158567751194 30.27386117530614, -97.74144154657606 30.28243151045525, -97.74023350199663 30.28252151468067, -97.7404345051003 30.2830438910299, -97.72644173188067 30.28727143486248, -97.72600866344004 30.28615796986944, -97.72071547151319 30.28705703595722, -97.72037933156265 30.2853407695101, -97.7100688189238 30.28393372738422, -97.71182414094548 30.27659253040514, -97.71291710431618 30.27672847223155, -97.71304358920513 30.2761965041207, -97.71314653040032 30.27568312378152, -97.71316521494255 30.27568497255121, -97.71341376642306 30.27463961873366, -97.71640141374144 30.27502500953458, -97.716191729408 30.27409533218606, -97.72197853142319 30.27298342950026))
```


</details>



## Enum Classes
There are a number of different enum classes used for both STAC requests and STAC items.





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac import enum
import inspect
[m for m in inspect.getmembers(enum) if not m[0].startswith('_') and m[0][0].isupper() and m[0] != 'IntFlag']
```


</details>







<details><summary>Expand Python Print-out</summary>


```text
    [('AssetType', <enum 'AssetType'>),
     ('Band', <enum 'Band'>),
     ('CloudPlatform', <enum 'CloudPlatform'>),
     ('Constellation', <enum 'Constellation'>),
     ('FilterRelationship', <enum 'FilterRelationship'>),
     ('Instrument', <enum 'Instrument'>),
     ('Mission', <enum 'Mission'>),
     ('Platform', <enum 'Platform'>),
     ('SortDirection', <enum 'SortDirection'>)]
```


</details>








<details><summary>Expand Python Code Sample</summary>


```python
# Specific to Queries
print("for defining the sort direction of a query")
for s in enum.SortDirection:
    print(s.name)
print("for defining the query relationship with a value (EQ, LTE, GTE, LT, GT, NEQ), a start-end range \n"
      "(BETWEEN, NOT_BETWEEN), a set (IN, NOT_IN) or a string (LIKE, NOT_LIKE). "
      "NOTE: EQ is the default relationship type")
for f in enum.FilterRelationship:
    print(f.name)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    for defining the sort direction of a query
    NOT_SORTED
    DESC
    ASC
    for defining the query relationship with a value (EQ, LTE, GTE, LT, GT, NEQ), a start-end range 
    (BETWEEN, NOT_BETWEEN), a set (IN, NOT_IN) or a string (LIKE, NOT_LIKE). NOTE: EQ is the default relationship type
    EQ
    LTE
    GTE
    LT
    GT
    BETWEEN
    NOT_BETWEEN
    NEQ
    IN
    NOT_IN
    LIKE
    NOT_LIKE
```


</details>







<details><summary>Expand Python Code Sample</summary>


```python
# Specific to Assets
print("these can be useful when getting a specific Asset from a STAC item by the type of Asset")
for a in enum.AssetType:
    print(a.name)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    these can be useful when getting a specific Asset from a STAC item by the type of Asset
    UNKNOWN_ASSET
    JPEG
    GEOTIFF
    LERC
    MRF
    MRF_IDX
    MRF_XML
    CO_GEOTIFF
    RAW
    THUMBNAIL
    TIFF
    JPEG_2000
    XML
    TXT
    PNG
    OVERVIEW
    JSON
    HTML
    WEBP
```


</details>







<details><summary>Expand Python Code Sample</summary>


```python
# STAC Item details
print("Mission, Platform and Instrument are aspects of data that can be used in queries.\n"
      "But as NSL currently only has one platform and one instrument, these may not be useful")
print("missions:")
for a in enum.Mission:
    print(a.name)
print("\nplatforms:")
for a in enum.Platform:
    print(a.name)
print("\ninstruments:")
for a in enum.Instrument:
    print(a.name)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    Mission, Platform and Instrument are aspects of data that can be used in queries.
    But as NSL currently only has one platform and one instrument, these may not be useful
    missions:
    UNKNOWN_MISSION
    LANDSAT
    NAIP
    SWIFT
    PNOA
    
    platforms:
    UNKNOWN_PLATFORM
    LANDSAT_1
    LANDSAT_2
    LANDSAT_3
    LANDSAT_123
    LANDSAT_4
    LANDSAT_5
    LANDSAT_45
    LANDSAT_7
    LANDSAT_8
    SWIFT_2
    SWIFT_3
    
    instruments:
    UNKNOWN_INSTRUMENT
    OLI
    TIRS
    OLI_TIRS
    POM_1
    TM
    ETM
    MSS
    POM_2
```


</details>



## Subscriptions and Data Delivery
This feature is useful if you want to be subscribed to a `StacRequest`, receiving published assets to a cloud bucket.

### Cloud Accounts


<details><summary>Expand Python Print-out</summary>


```text
    - AWS id: `275780812376`
    - GCP email: `thirdparty-bucket-access@swiftera-processed-data.iam.gserviceaccount.com`
```


</details>


### Example

Set up for the destination bucket is slightly different between AWS and GCP, so we'll review both.

Assume that we have an upcoming flight covering Austin, TX and you'd like only some STAC items to be copied to your 
bucket as they're published:





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime, timezone

from nsl.stac import enum
from nsl.stac.destinations import AWSDestination, GCPDestination
from nsl.stac.experimental import StacRequestWrap, NSLClientEx

# get a client interface to the gRPC channel
client_ex = NSLClientEx()

# create a new request
request = StacRequestWrap()
# a polygon containing two University of Texas at Austin stadiums
request.intersects = Polygon.import_wkt('POLYGON((-97.73521184921263 30.28551192777313,'
                                        '-97.73522257804868 30.279369307168608,'
                                        '-97.72501945495603 30.279313716086122,'
                                        '-97.7251052856445 30.285530456966953,'
                                        '-97.73521184921263 30.28551192777313))',
                                        epsg=4326)
# we only want images delivered after the flight was conducted
request.set_observed(rel_type=enum.FilterRelationship.GTE, value=datetime(2021, 11, 1, tzinfo=timezone.utc))
```


</details>



### GCP Delivery

The destination bucket preparation process for GCP is fairly simple:

1. Create a GCP Role with only `storage.objectAdmin` permissions for your bucket (e.g. `my-bucket`).

2. Assign the newly created role (e.g. `NSLSubscription`) to our GCP service account,
`thirdparty-bucket-access@swiftera-processed-data.iam.gserviceaccount.com`. This can be done from the terminal, e.g.:

```bash
$ gsutil iam ch \
    serviceAccount:thirdparty-bucket-access@swiftera-processed-data.iam.gserviceaccount.com:roles/storage.objectAdmin \
    gs://my-bucket
```

Finally, lets create a `BaseDestination` object and finish creating our subscription:





<details><summary>Expand Python Code Sample</summary>


```python
# creates a destination object to describe how assets should be delivered
dst = GCPDestination(asset_type=enum.AssetType.GEOTIFF, # GEOTIFF by default, can also be THUMBNAIL
                     bucket='my-bucket',                # the name of your bucket
                     region='us-central1',              # region your bucket is located in
                     save_directory='/')                # directory in which assets will be copied, <stac_id>.<file_ext>

# create the subscription, returning its id
sub_id = client_ex.subscribe_ex(request, destination=dst)
print(sub_id)

# retrieve all of your current subscriptions, viewing the most recent
subs = client_ex.subscriptions_ex()
most_recent_sub = subs[len(subs) - 1]
print(most_recent_sub)

# deactivate a subscription, pausing all deliveries
client_ex.unsubscribe_ex(sub_id=sub_id)

# reactivate a subscription, resuming all deliveries
client_ex.resubscribe_ex(sub_id=sub_id)

```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    created subscription with id: Njg1NjJlMmYtMTE5Ny00NjMyLThhMDAtZDNlYzY1MjViMWEw
    Njg1NjJlMmYtMTE5Ny00NjMyLThhMDAtZDNlYzY1MjViMWEw
    <nsl.stac.subscription.Subscription object at 0x7f64580d93d0>
    deactivated subscription with id: Njg1NjJlMmYtMTE5Ny00NjMyLThhMDAtZDNlYzY1MjViMWEw
    reactivated subscription with id: Njg1NjJlMmYtMTE5Ny00NjMyLThhMDAtZDNlYzY1MjViMWEw
```


</details>



### AWS Delivery

The destination bucket preparation process for AWS is slightly more involved. We're ultimately going to create an AWS
IAM Role (e.g. `NSLDelivery`) to be assumed by NSL's AWS account,
and an accompanying policy giving NSL's AWS account access to the destination bucket (e.g. `my-bucket`).
  
1. In your AWS account where the bucket is located, browse to IAM service.
  
2. Choose Roles -> "Create role". Choose "Another AWS account", providing NSL's AWS account ID: `275780812376`.
  
3. Click next to Permissions
  
4. Click "Create Policy", select the tab "JSON" and adjust the template below, which will whitelist actions NSL can
perform on your chosen destination bucket.
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-bucket"
    },
    {
      "Sid": "VisualEditor1",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```
  
5. Click "Next: Tags", adding any optional tags.
  
6. Name this policy (e.g. `NSLBucketAccess`), and finally click "Create policy" to finish creating the policy.
  
7. Go back to Roles, refresh, and then select the `NSLBucketAccess` policy you just created.
  
8. Now we're back to finalizing the creation of the Role, so give it a meaningful name, e.g. `NSLBucketDeliverer`.

9. Contact us so we can update our AWS account to assume this role and begin deliveries. 

Finally, lets create a `BaseDestination` object and finish creating our subscription:





<details><summary>Expand Python Code Sample</summary>


```python
# creates a destination object to describe how assets should be delivered
dst = AWSDestination(asset_type=enum.AssetType.GEOTIFF, # GEOTIFF by default, can also be THUMBNAIL
                     role_arn='arn:aws:iam::<YOUR_ACCESS_KEY_ID>:role/NSLBucketDeliverer',
                     bucket='my-bucket',                # the name of your bucket
                     region='us-central1',              # region your bucket is located in
                     save_directory='/')                # directory in which assets will be copied, <stac_id>.<file_ext>

# create the subscription, returning its id
sub_id = client_ex.subscribe_ex(request, destination=dst)
print(sub_id)

# retrieve all of your current subscriptions, viewing the most recent
subs = client_ex.subscriptions_ex()
most_recent_sub = subs[len(subs) - 1]
print(most_recent_sub)

# deactivate a subscription, pausing all deliveries
client_ex.unsubscribe_ex(sub_id=sub_id)

# reactivate a subscription, resuming all deliveries
client_ex.resubscribe_ex(sub_id=sub_id)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    created subscription with id: NDM3ZTAzZjQtY2Q4Yy00ZTJmLTk3YzUtYTYzOGJhNDNiODJj
    NDM3ZTAzZjQtY2Q4Yy00ZTJmLTk3YzUtYTYzOGJhNDNiODJj
    <nsl.stac.subscription.Subscription object at 0x7f6458152e80>
    deactivated subscription with id: NDM3ZTAzZjQtY2Q4Yy00ZTJmLTk3YzUtYTYzOGJhNDNiODJj
    reactivated subscription with id: NDM3ZTAzZjQtY2Q4Yy00ZTJmLTk3YzUtYTYzOGJhNDNiODJj
```


</details>


