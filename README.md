# gRPC stac-client-python

## What is this Good for
Use this library to query for Near Space Labs aerial imagery by area of interest, date observed and other details. You can also use this library and your credentials to download Near Space Labs Geotiffs and Thumbnails for every scene we've collected. This client accesses [Near Space Labs](https://nearspacelabs.com)' gRPC STAC service (or any gRPC STAC service) for metadata queries. The best way to get familiar with the Near Space Labs client is to pip install the `nsl.stac` package and use the [Jupyter Notebooks provided](#running-included-jupyter-notebooks) (README.ipynb, Examples.ipynb, StacItem.ipynb).

To get access to our high resolution Austin, Texas imagery, get a client id and secret [here](https://www.nearspacelabs.com/#nearspacelabs).

## Sections
- [Setup](#setup)
- [Credentials](#credentials)
- [First Code Example](#first-code-example)
- [STAC metadata structure](#what-are-protobufs-grpc-and-spatio-temporal-asset-catalogs)
  - [Assets](#assets-images-to-download)
  - [Stac Item In Depth](./StacItem.md)
- [Queries](#queries)
  - [Simple](#simple-query-and-the-makeup-of-a-stacitem)
  - [Spatial](#spatial-queries)
  - [Temporal](#temporal-queries)
  - [Advanced Examples](./AdvancedExamples.md)
  - [Experimental](./Experimental.md)
- [Downloading](#downloading)
  - [Thumbnails](#thumbnails)
  - [Geotiffs](#geotiffs)
  - [Handling Deadlines](#handling-deadlines)
- [gRPC STAC vs REST STAC](#differences-between-grpcprotobuf-stac-and-openapijson-stac)

## Setup
**WARNING** You'll need to have Python3 installed (nsl.stac **does not** work with Python2). If you have multiple versions of Python and pip on your operating system, you may need to use `python3` and `pip3` in the below installation commands.

Grab `nsl.stac` from [pip](https://pypi.org/project/nsl.stac/):
```bash
pip install nsl.stac
```

**OR** Install it from source:
```bash
pip install -r requirements.txt
python setup.py install
```

### Environment Variables
There are a few environment variables that the stac-client-python library relies on for accessing the STAC service:

- `NSL_ID` and `NSL_SECRET`, if you're downloading Near Space Labs data you'll need credentials.
- `STAC_SERVICE`, (not required) If left unset it defaults to "api.nearspacelabs.net:9090". This is the address of the STAC metadata service.

### Running Included Jupyter Notebooks
If you are using a virtual environment, but the jupyter you use is outside that virtual env, then you'll have to add your virtual environment to jupyter using something like `python -m ipykernel install --user --name=myenv` (more [here](https://janakiev.com/blog/jupyter-virtual-envs/)). Your best python life is no packages installed globally and always living virtual environment to virtual environment.

Install the requirements for the demo:

```bash

pip install -r requirements-demo.txt

```

On Mac or Linux you can run Jupyter notebook with your environment variables set for `NSL_ID` and `NSL_SECRET`:

```bash

NSL_ID="YOUR_ID" NSL_SECRET="YOUR_SECRET" jupyter notebook

```

If you're on windows you'll need to set your environment variables using the `SET` command or in the [system environment variables gui](https://www.hows.tech/2019/03/how-to-set-environment-variables-in-windows-10.html). Then call `jupyter notebook`.

### Rate Limiting and Timeouts
To keep our services available to may simulataneous customers, we've implemented rate limiting for API requests and timeouts for long-standing requests. 

At this release our timeouts are 15 seconds. If you use the `search` method, you're maintaining an open connection with the server while retrieving STAC items. If you have a sub-routine that is taking longer than 15 seconds, then you might want to circumvent the timeout by collecting all the STAC items in a `list` and then executing your sub-routine. An example of this can be seen in the [Handling Deadlines](#handling-deadlines) docs for downloads.

If you are returning so many stac items that you are timing out then you may want to use a `limit` and `offset` variables in the `StacRequest`. For more details about `limit` and `offset` visit the [AdvancedExamples.md](./AdvancedExamples.md) doc.

For our download API we've implemented a 4 requests per second limit. You may need implement a retry mechanism with an [exponential backoff](https://en.wikipedia.org/wiki/Exponential_backoff) if you are overruning the rate limit.

## Credentials
There are three ways to set credentials. The first is to set them using environment variables `NSL_ID` and `NSL_SECRET`. You can also create a `.nsl` directory in your home directory and create a `credentials` file with a profile name in brackets and the `NSL_ID` and `NSL_SECRET` defined below that. For example the contents of the `~/.nsl/credentials` file would look like the below example: 

```
[default]
NSL_ID=YOUR_NSL_ID
NSL_SECRET=YOUR_NSL_SECRET
```

A second alternative to environment variables or the credentials file is to use the `set_credentials` method on the `NSLClient` object. For example:
```
client = NSLClient()
client.set_credentials(nsl_id='YOUR_NSL_ID', nsl_secret='YOUR_NSL_SECRET')
```
The `NSLClient()` call accesses a module initialized "singleton". gRPC prefers that only one TCP/IP connection be open and that's why the `NSLClient()` call accesses a single instance of the client. If a single instance of NSLClient is shared by multiple users with different `NSL_ID` and `NSL_SECRET`, those credentials can be added using `set_credentials`. After that, specifiying the `NSL_ID` in the calls to `search_one`, `search`, `count` and the download methods in the `nsl.stac.utils` module.
```
# ADVANCED EXAMPLE. 
# only for users that have multiple credentials being used within one single instance
import tempfile
from nsl.stac import NSLClient, StacRequest
from nsl.stac.utils import download_href_object
client = NSLClient()
# first credentials set
client.set_credentials(nsl_id='YOUR_NSL_ID', nsl_secret='YOUR_NSL_SECRET')
# second crerdentials set
client.set_credentials(nsl_id='YOUR_NSL_ID_2', nsl_secret='YOUR_NSL_SECRET_2')
stac_request = StacRequest()
# request using first credential
item = client.search_one(stac_request, nsl_id='YOUR_NSL_ID')
# request using second credential
item = client.search_one(stac_request, nsl_id='YOUR_NSL_ID_2')
```


## First Code Example
Want to jump quickly into a code sample for searching by area of interest and date range, and then downloading a Geotiff? Expand the below sections to examine a code block using our STAC client and the printout from it's execution. If you need to read more about STAC first, then jump to the summary [here](#what-are-protobufs-grpc-and-spatio-temporal-asset-catalogs). 

This call will take a little bit to execute as it downloads an image.





<details><summary>Expand Python Code Sample</summary>


```python
import tempfile
from IPython.display import Image, display
from datetime import date
from nsl.stac import StacRequest, GeometryData, ProjectionData
from nsl.stac import enum, utils
from nsl.stac.client import NSLClient

# the client package stubs out a little bit of the gRPC connection code 
# get a client interface to the gRPC channel. This client singleton is threadsafe
client = NSLClient()

# our area of interest will be the coordinates of the UT Stadium in Austin, Texas
# the order of coordinates here is longitude then latitude (x, y). The results of our query 
# will be returned only if they intersect this point geometry we've defined (other geometry 
# types besides points are supported)
# This string format, POINT(float, float) is the well-known-text geometry format:
# https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
ut_stadium_wkt = "POINT(-97.7323317 30.2830764)"
# GeometryData is a protobuf container for GIS geometry information, the epsg in the spatial 
# reference defines the WGS-84 ellipsoid (`epsg=4326`) spatial reference (the latitude longitude 
# spatial reference most commonly used)
geometry_data = GeometryData(wkt=ut_stadium_wkt, proj=ProjectionData(epsg=4326))

# TimestampField is a query field that allows for making sql-like queries for information
# LTE is an enum that means less than or equal to the value in the query field
# Query data from August 25, 2019
time_filter = utils.pb_timestampfield(value=date(2019, 8, 25), rel_type=enum.FilterRelationship.LTE)

# the StacRequest is a protobuf message for making filter queries for data
# This search looks for any type of imagery hosted in the STAC service that intersects the austin 
# capital area of interest and was observed on or before August 25, 2019
stac_request = StacRequest(datetime=time_filter, intersects=geometry_data)

# search_one method requests only one item be returned that meets the query filters in the StacRequest 
# the item returned is a StacItem protobuf message. search_one, will only return the most recently 
# observed results that matches the time filter and spatial filter
stac_item = client.search_one(stac_request)

# get the thumbnail asset from the assets map. The other option would be a Geotiff, 
# with asset key 'GEOTIFF_RGB'
asset = utils.get_asset(stac_item, asset_type=enum.AssetType.THUMBNAIL)

with tempfile.TemporaryDirectory() as d:
    filename = utils.download_asset(asset=asset, save_directory=d)
    display(Image(filename=filename))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    nsl client connecting to stac service at: api.nearspacelabs.net:9090
    
    attempting NSL authentication against api.nearspacelabs.net
    fetching new authorization in 60 minutes
```


</details>




![png](README_files/README_1_1.png)


In the above example, the [StacRequest](https://geo-grpc.github.io/api/#epl.protobuf.StacRequest) holds spatial and temporal query parameters for searching for [StacItems](https://geo-grpc.github.io/api/#epl.protobuf.StacItem). The `client.search_one` method makes requests to the [StacService's](https://geo-grpc.github.io/api/#epl.protobuf.StacService) SearchOne gRPC method. In this case you can see that we've connected to the `eap.nearspacelabs.net` STAC service. In the next section we go into more detail about Protobufs, gRPC, and STAC.

## What are Protobufs, gRPC, and Spatio Temporal Asset Catalogs? 
This python client library is used for connecting to a gRPC enabled STAC service. STAC items and STAC requests are Protocol Buffers (protobuf) instead of traditional JSON.

Never heard of gRPC, Protocol Buffers or STAC? Below are summary blurbs and links for more details about these open source projects.

Definition of STAC from https://stacspec.org/:
> The SpatioTemporal Asset Catalog (STAC) specification provides a common language to describe a range of geospatial information, so it can more easily be indexed and discovered.  A 'spatiotemporal asset' is any file that represents information about the earth captured in a certain space and time.

Definition of gRPC from https://grpc.io
> gRPC is a modern open source high performance RPC framework that can run in any environment. It can efficiently connect services in and across data centers with pluggable support for load balancing, tracing, health checking and authentication. It is also applicable in last mile of distributed computing to connect devices, mobile applications and browsers to backend services.

Definitions of Protocol Buffers (protobuf) from https://developers.google.com/protocol-buffers/
> Protocol buffers are Google's language-neutral, platform-neutral, extensible mechanism for serializing structured data – think XML, but smaller, faster, and simpler. You define how you want your data to be structured once, then you can use special generated source code to easily write and read your structured data to and from a variety of data streams and using a variety of languages.

In other words:
- You can think of Protobuf as a strict data format like xml or JSON + linting, except Protobuf is a compact binary message with strongly typed fields
- gRPC is similar to REST + OpenAPI, except gRPC is an [RPC](https://en.wikipedia.org/wiki/Remote_procedure_call) framework that supports bi-directional streaming
- STAC is a specification that helps remove repeated efforts for searching geospatial datasets (like WFS for specific data types)

### Assets (Images to Download)
In STAC, Assets can be any file type. For our Near Space Labs Swift dataset an asset can be an RGB Geotiff (selected using the `GEOTIFF_RGB` asset key) or an RGB thumbnail (selected using the `THUMBNAIL_RGB` asset key).

* [Example of Downloading a Geotiff](#first-code-example)
* [Example of Downloading a Thumbnail](#downloading)

## Queries

### Simple Query and the Makeup of a StacItem
The easiest query to construct is a `StacRequest` constructor with no variables, and the next simplest, is the case where we know the STAC item `id` that we want to search. If we already know the STAC `id` of an item, we can construct the `StacRequest` as follows:





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.client import NSLClient
from nsl.stac import StacRequest
# get a client interface to the gRPC channel
client = NSLClient()

stac_request = StacRequest(id='20190822T183518Z_746_POM1_ST2_P')

# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)
print(stac_item)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    id: "20190822T183518Z_746_POM1_ST2_P"
    collection: "NSL_SCENE"
    properties {
      type_url: "type.googleapis.com/st.protobuf.v1.NslData"
      value: "\n\340\014\n\03620190822T162258Z_TRAVIS_COUNTY\"\003 \352\0052\03520200702T102306Z_746_ST2_POM1:\03520190822T183518Z_746_POM1_ST2:\03520200702T101632Z_746_ST2_POM1:\03520200702T102302Z_746_ST2_POM1:\03520200702T102306Z_746_ST2_POM1B\03520190822T183518Z_746_POM1_ST2H\001R\374\n\n$\004\304{?\216\371\350=\376\377\306>\300\327\256\275\323rv?2\026*D3Qy6\177>\3675\000\000\200?\022\024\r+}\303\302\025\033;\362A\0353}\367\300%g\232\250@\022\024\r\026}\303\302\025\376?\362A\035\000\367\235@%\232\t\331?\022\024\r\351|\303\302\025\021A\362A\035M\370\033\301%g\016\226\277\022\024\r\201|\303\302\025\3709\362A\035\000\252\245@%\315\3547?\022\024\r\310|\303\302\025\245G\362A\035\232\315l\301%3\347\270\300\022\024\rq|\303\302\025\2149\362A\035\000\376o@%\000(\017@\022\024\rD|\303\302\025oD\362A\0353\323\302\301%\315\306\230\300\022\024\r\031|\303\302\025\035=\362A\035g\277$A%\000\340\231?\022\024\rE|\303\302\025\215I\362A\0353\275z\300%g\020\236\300\022\024\r\345{\303\302\0258C\362A\035\0008\242?%\232\231\226\277\022\024\r\010|\303\302\025!I\362A\0353\377\212\300%\000V\241\300\022\024\r|{\303\302\025\207F\362A\0353\203Y@%\315,\313\276\022\024\r\001{\303\302\025FJ\362A\035g^\025@%\315\010\214?\022\024\r\313z\303\302\025\353H\362A\0353\3377@%g\326\325\277\022\024\rjz\303\302\025\260@\362A\035\315F\006A%g\246[\277\022\024\r\035z\303\302\0254E\362A\035\232\001|@%\232!\265?\022\024\r\330y\303\302\025\320@\362A\0353Sa\300%\000@\245>\022\024\r\362y\303\302\025zE\362A\035\232\221\020\300%3U\206@\022\024\r\337y\303\302\025\210F\362A\035g\246l?%gf\234\276\022\024\r\335y\303\302\025aF\362A\035\000\260\023@%\315,#\277\022\024\r\321y\303\302\025\234F\362A\035\000 7@%\232!\221?\022\024\r\307y\303\302\025\177F\362A\035\232\371\371?%\315\224\225?\022\024\r\213y\303\302\025\350@\362A\0353\'\343\300%3g&\300\022\024\r\300y\303\302\025\tF\362A\035\315h\312@%g\266\013?\022\024\r_y\303\302\025\236A\362A\035\315\340\311@%3\363j>\022\024\r\271x\303\302\025G?\362A\0353\334\272\301%gb\201\300\022\024\r\307x\303\302\025WG\362A\035\000|6\301%\232\231i>\022\024\r\200x\303\302\025\016F\362A\035\315\007\244\301%\315L\000>\022\024\rqx\303\302\025jI\362A\035\315\254\007\301%\232E\247?\022\024\rjx\303\302\025(I\362A\035\232\305\000\301%\315L\'>\022\024\r\027x\303\302\025\356A\362A\035\232I\246?%\315\004\246\277\022\024\r\010x\303\302\025AB\362A\035\232y\305\300%\315\3740?\022\024\r\032x\303\302\0257D\362A\0353\003\275\277%\232\311.?\022\024\r\002x\303\302\025&C\362A\035\315\014\301\277%g*2@\022\024\r\361w\303\302\025\330B\362A\035\000T\347\300%\232\235\025\300\022\024\r\372v\303\302\025\030<\362A\0353\323\364?%gNt\300\022\024\r;w\303\302\025\273I\362A\03533\335>%\232\025\213?\022\024\r\324v\303\302\025QC\362A\035\315,\305\277%\232\375\035@\022\024\r\340v\303\302\025@G\362A\035\315@\234\300%\232)\342?\022\024\r\312v\303\302\025yC\362A\035\315\214\247\276%g\246\375>\022\024\r\222v\303\302\025\233A\362A\035\315\334\244?%g\366\035\277\022\024\r\256v\303\302\025\\F\362A\0353G\204@%\232A\017@\022\024\rov\303\302\025\215=\362A\035\232\325\340@%3\263\033\276\022\024\r\206v\303\302\025SC\362A\0353\263k?%3\363\177\276\022\024\r\267v\303\302\025NK\362A\035\315\0148\277%3\323\000>\022\024\r\255v\303\302\025kK\362A\035gf4\277%\000\312\201\277\022\024\r)v\303\302\025\316=\362A\035\232\271Z\277%\315\014\375\277\022\024\r_v\303\302\025\356H\362A\035\315\004n@%3\243\240\276\022\024\r7v\303\302\025\350H\362A\0353#\212@%g~\272?\022\024\r\314u\303\302\025Y;\362A\035\000\000F=%gF\253?\022\024\r\276u\303\302\025q>\362A\0353/\234\300%g\246T\277\022\024\r\266u\303\302\025\321>\362A\035\315 \272\300%3SW\300\022\024\r\307u\303\302\025\211A\362A\035\000$\264\300%3\243\r\277\022\024\r\360u\303\302\025RK\362A\0353\347\231@%\315\325\036\300\022\024\r\262u\303\302\025\035F\362A\0353\2633\276%\232i3?\032#m_3009743_sw_14_1_20160928_20161129\"Y\t&\2068NM\357\"A\021\003\3272rL\217IA\031\267G\014x\260\375\"A!\202I\225>\020\222IA*3\0221+proj=utm +zone=14 +datum=NAD83 +units=m +no_defs*\005\r\205[\"A2\005\r\000\356\\@:\005\r\227\210\306AB\005\r\205E\257@\022Q\n e502fe83507f0d28c826f33619a678e9\022\03120200806T033934Z_SWIFTERA\030\010(A0\0018\340\025@\330\247\004H\270\275\004X\263\027"
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
      seconds: 1598623843
      nanos: 801001892
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



The above print out for the stac item is quite lengthy. Although `stac_item` is a protobuf object, it's `__str__` method prints out a JSON-like object. You can see in the below example that this `StacItem` contains the following:
- [GeometryData](https://geo-grpc.github.io/api/#epl.protobuf.v1.GeometryData) which is defined with a WGS-84 well-known binary geometry
- [EnvelopeData](https://geo-grpc.github.io/api/#epl.protobuf.v1.EnvelopeData) which is also WGS-84
- [Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) Google's protobuf unix time format
- [Eo](https://geo-grpc.github.io/api/#epl.protobuf.v1.Eo) for electro-optical sensor details
- [Landsat](https://geo-grpc.github.io/api/#epl.protobuf.v1.Landsat) for Landsat specific details
- an array map of [StacItem.AssetsEntry](https://geo-grpc.github.io/api/#epl.protobuf.v1.StacItem.AssetsEntry) with each [Asset](https://geo-grpc.github.io/api/#epl.protobuf.v1.Asset) containing details about [AssetType](https://geo-grpc.github.io/api/#epl.protobuf.v1.AssetType), Electro Optical [Band enums](https://geo-grpc.github.io/api/#epl.protobuf.v1.Eo.Band) (if applicable), and other details for downloading and interpreting data

You may have noticed that the [Asset](https://geo-grpc.github.io/api/#epl.protobuf.v1.Asset) in the above python print out has a number of additional parameters not included in the JSON STAC specification. 

### Spatial Queries
The STAC specification has a bounding box `bbox` specification for STAC items. Here we make a STAC request using a bounding box. One slight difference from JSON STAC, is that we define an [EnvelopeData](https://geo-grpc.github.io/api/#epl.protobuf.v1.EnvelopeData) protobuf object. This allows us to use other projections besides WGS84





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac import StacRequest, EnvelopeData, ProjectionData
from nsl.stac.client import NSLClient

client = NSLClient()

# define our area of interest bounds using the xmin, ymin, xmax, ymax coordinates of an area on 
# the WGS-84 ellipsoid
neighborhood_box = (-97.7352547645, 30.27526474757116, -97.7195692, 30.28532)
# here we define our envelope_data protobuf with bounds and a WGS-84 (`epsg=4326`) spatial reference
envelope_data = EnvelopeData(xmin=neighborhood_box[0], 
                             ymin=neighborhood_box[1], 
                             xmax=neighborhood_box[2], 
                             ymax=neighborhood_box[3],
                             proj=ProjectionData(epsg=4326))
# Search for data that intersects the bounding box
stac_request = StacRequest(bbox=envelope_data)


for stac_item in client.search(stac_request):
    print("STAC item id: {}".format(stac_item.id))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20200703T174443Z_650_POM1_ST2_P
    STAC item id: 20200703T174303Z_595_POM1_ST2_P
    STAC item id: 20200703T174258Z_592_POM1_ST2_P
    STAC item id: 20200703T174234Z_579_POM1_ST2_P
    STAC item id: 20200703T174155Z_558_POM1_ST2_P
    STAC item id: 20200703T174034Z_516_POM1_ST2_P
    STAC item id: 20200703T174032Z_515_POM1_ST2_P
    STAC item id: 20200703T174028Z_513_POM1_ST2_P
    STAC item id: 20200703T174021Z_509_POM1_ST2_P
    STAC item id: 20200703T174019Z_508_POM1_ST2_P
```


</details>



Above should be printed the STAC ids of 10 items (10 is the default limit for the service we connected to).

#### Query By GeoJSON

Next we want to try searching by geometry instead of bounding box. We'll use a geojson to define our [GeometryData](https://geo-grpc.github.io/api/#epl.protobuf.v1.GeometryData) protobuf. GeometryData can be defined using geojson, wkt, wkb, or esri_shape:





<details><summary>Expand Python Code Sample</summary>


```python
import json
import requests

from nsl.stac import StacRequest, GeometryData, ProjectionData
from nsl.stac.client import NSLClient
client = NSLClient()

# request the geojson footprint of Travis County, Texas
url = "http://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/TX/Travis.geo.json"
r = requests.get(url)
travis_geojson = json.dumps(r.json()['features'][0]['geometry'])
# create our GeometryData protobuf from geojson string and WGS-84 ProjectionData protobuf
geometry_data = GeometryData(geojson=travis_geojson, 
                             proj=ProjectionData(epsg=4326))
# Search for data that intersects the geojson geometry and limit results 
# to 2 (instead of default of 10)
stac_request = StacRequest(intersects=geometry_data, limit=2)
# collect the ids from STAC items to compare against results from wkt GeometryData
geojson_ids = []

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item id: {}".format(stac_item.id))
    geojson_ids.append(stac_item.id)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20201001T211834Z_2012_POM1_ST2_P
    STAC item id: 20201001T211832Z_2011_POM1_ST2_P
```


</details>



#### Query By WKT

Same geometry as above, but a wkt geometry instead of a geojson:





<details><summary>Expand Python Code Sample</summary>


```python
# Same geometry as above, but a wkt geometry instead of a geojson
travis_wkt = "POLYGON((-97.9736 30.6251, -97.9188 30.6032, -97.9243 30.5703, -97.8695 30.5484, \
              -97.8476 30.4717, -97.7764 30.4279, -97.5793 30.4991, -97.3711 30.4170, \
              -97.4916 30.2089, -97.6505 30.0719, -97.6669 30.0665, -97.7107 30.0226, \
              -98.1708 30.3567, -98.1270 30.4279, -98.0503 30.6251))" 
geometry_data = GeometryData(wkt=travis_wkt, 
                             proj=ProjectionData(epsg=4326))
stac_request = StacRequest(intersects=geometry_data, limit=2)
for stac_item in client.search(stac_request):
    print("STAC item id: {0} from wkt filter intersects result from geojson filter: {1}"
          .format(stac_item.id, stac_item.id in geojson_ids))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20201001T211834Z_2012_POM1_ST2_P from wkt filter intersects result from geojson filter: True
    STAC item id: 20201001T211832Z_2011_POM1_ST2_P from wkt filter intersects result from geojson filter: True
```


</details>



### Temporal Queries
When it comes to Temporal queries there are a few things to note. One is that we are using Google's [Timestamp proto](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) to define the temporal aspect of STAC items. This means time is stored with an `int64` for seconds and an `int32` for nanoseconds relative to an epoch at UTC midnight on January 1, 1970.

So when you read the time fields on a [StacItem](https://geo-grpc.github.io/api/#epl.protobuf.v1.StacItem), you'll notice that `datetime`, `observed`, `created`, and `processed` all use the Timestamp Protobuf object.

When creating a time query filter, we want to use the >, >=, <, <=, ==, != operations and inclusive and exclusive range requests. We do this by using a [TimestampFilter](https://geo-grpc.github.io/api/#epl.protobuf.v1.TimestampFilter), where we define the value using the `value` field or the `start`&`end` fields. And then we define a relationship type using the `rel_type` field and the [FilterRelationship](https://geo-grpc.github.io/api/#epl.protobuf.v1.FilterRelationship) enum values of `EQ`, `LTE`, `GTE`, `LT`, `GT`, `BETWEEN`, `NOT_BETWEEN`, or `NEQ`.

#### Everything After A Specific Date





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import date, datetime, timezone
from nsl.stac.client import NSLClient
from nsl.stac import utils, StacRequest, enum

# make a filter that selects all data on or after August 21st, 2019
value = date(2019, 8, 21)
time_filter = utils.pb_timestampfield(value=value, rel_type=enum.FilterRelationship.GTE)
stac_request = StacRequest(datetime=time_filter, limit=2)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item date, {0}, is after {1}: {2}".format(
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(time_filter.value.seconds, tz=timezone.utc).isoformat(),
        stac_item.observed.seconds > time_filter.start.seconds))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item date, 2020-12-08T17:48:48+00:00, is after 2019-08-21T00:00:00+00:00: True
    STAC item date, 2020-12-08T17:48:46+00:00, is after 2019-08-21T00:00:00+00:00: True
```


</details>



The above result shows the datetime of the STAC item, the datetime of the query and a confirmation that they satisfy the query filter. Notice the warning, this is because our date doesn't have a timezone associated with it. By default we assume UTC.

#### Everything Between Two Dates

Now we're going to do a range request and select data between two dates using the `start` and `end` parameters instead of the `value` parameter:





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime, timezone, timedelta
from nsl.stac.client import NSLClient
from nsl.stac import utils, enum, StacRequest
# Query data from August 1, 2019
start = datetime(2019, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
# ... up until August 10, 2019
end = start + timedelta(days=9)
time_filter = utils.pb_timestampfield(start=start, end=end, rel_type=enum.FilterRelationship.BETWEEN)

stac_request = StacRequest(datetime=time_filter, limit=2)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item date, {0}, is before {1}: {2}".format(
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(time_filter.end.seconds, tz=timezone.utc).isoformat(),
        stac_item.observed.seconds < time_filter.end.seconds))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item date, 2019-08-06T20:42:53+00:00, is before 2019-08-10T00:00:00+00:00: True
    STAC item date, 2019-08-06T20:42:51+00:00, is before 2019-08-10T00:00:00+00:00: True
```


</details>



In the above print out we are returned STAC items that are between the dates of Aug 1 2019 and Aug 10 2019. Also, notice there's no warnings as we defined our utc timezone on the datetime objects.

#### Select Data for One Day

Now we'll search for everything on a specific day using a python `datetime.date` for the `value` and `rel_type` set to  use equals (`FilterRelationship.EQ`). Python's `datetime.datetime` is a specific value and if you use it combined with `EQ` the query would insist that the time relationship match down to the second. But since `datetime.date` is only specific down to the day, the filter is created for the entire day. This will check for everything from the start until the end of the 8th of August, specifically in the Austin, Texas timezone (UTC -6).





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime, timezone, timedelta, date
from nsl.stac.client import NSLClient
from nsl.stac import utils, enum, StacRequest
# Query all data for the entire day of August 6, 2019
value = date(2019, 8, 6)
# if you omit this tzinfo from the pb_timestampfield function, the default for tzinfo 
# is assumed to be utc 
texas_utc_offset = timezone(timedelta(hours=-6))
time_filter = utils.pb_timestampfield(rel_type=enum.FilterRelationship.EQ,
                                      value=value,
                                      tzinfo=texas_utc_offset)

stac_request = StacRequest(datetime=time_filter, limit=2)

# get a client interface to the gRPC channel
client = NSLClient()
for stac_item in client.search(stac_request):
    print("STAC item date, {0}, is before {1}: {2}".format(
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(time_filter.end.seconds, tz=texas_utc_offset).isoformat(),
        stac_item.observed.seconds < time_filter.end.seconds))
    print("STAC item date, {0}, is after {1}: {2}".format(
        datetime.fromtimestamp(stac_item.observed.seconds, tz=timezone.utc).isoformat(),
        datetime.fromtimestamp(time_filter.start.seconds, tz=texas_utc_offset).isoformat(),
        stac_item.observed.seconds > time_filter.start.seconds))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item date, 2019-08-06T20:42:53+00:00, is before 2019-08-06T23:59:59-06:00: True
    STAC item date, 2019-08-06T20:42:53+00:00, is after 2019-08-06T00:00:00-06:00: True
    STAC item date, 2019-08-06T20:42:51+00:00, is before 2019-08-06T23:59:59-06:00: True
    STAC item date, 2019-08-06T20:42:51+00:00, is after 2019-08-06T00:00:00-06:00: True
```


</details>



The above printout demonstrates that the results are between the time ranges of `2019-08-06T00:00:00-06:00` and `2019-08-06T23:59:59-06:00`.

## Downloading
To download an asset use the `bucket` + `object_path` or the `href` fields from the asset, and download the data using the library of your choice. There is also a download utility in the `nsl.stac.utils` module. Downloading from Google Cloud Storage buckets requires having defined your `GOOGLE_APPLICATION_CREDENTIALS` [environment variable](https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable). Downloading from AWS/S3 requires having your configuration file or environment variables defined as you would for [boto3](https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/quickstart.html#configuration). 

### Thumbnails
To downlad thumbnail assets follow the pattern in the below example:





<details><summary>Expand Python Code Sample</summary>


```python
import tempfile
from IPython.display import Image, display

from nsl.stac.client import NSLClient
from nsl.stac import utils, enum, StacRequest, GeometryData, ProjectionData

mlk_blvd_wkt = 'LINESTRING(-97.72842049283962 30.278624772098176,-97.72142529172878 30.2796624743974)'
geometry_data = GeometryData(wkt=mlk_blvd_wkt, 
                             proj=ProjectionData(epsg=4326))
time_filter = utils.pb_timestampfield(value=date(2019, 8, 25), rel_type=enum.FilterRelationship.LTE)
stac_request = StacRequest(intersects=geometry_data,
                           datetime=time_filter,
                           limit=3)

# get a client interface to the gRPC channel
client = NSLClient()

for stac_item in client.search(stac_request):
    # get the thumbnail asset from the assets map
    asset = utils.get_asset(stac_item, asset_type=enum.AssetType.THUMBNAIL)
    # (side-note delete=False in NamedTemporaryFile is only required for windows.)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as file_obj:
        utils.download_asset(asset=asset, file_obj=file_obj)
        display(Image(filename=file_obj.name))
```


</details>




![png](README_files/README_18_0.png)



![png](README_files/README_18_1.png)



![png](README_files/README_18_2.png)


### Geotiffs
To download the full geotiff asset follow the pattern in the below example:





<details><summary>Expand Python Code Sample</summary>


```python
import os
import tempfile
from datetime import date
from nsl.stac import StacRequest, GeometryData, ProjectionData, enum
from nsl.stac import utils
from nsl.stac.client import NSLClient

client = NSLClient()

ut_stadium_wkt = "POINT(-97.7323317 30.2830764)"
geometry_data = GeometryData(wkt=ut_stadium_wkt, proj=ProjectionData(epsg=4326))

# Query data from before September 1, 2019
time_filter = utils.pb_timestampfield(value=date(2019, 9, 1), rel_type=enum.FilterRelationship.LTE)

stac_request = StacRequest(datetime=time_filter, intersects=geometry_data)

stac_item = client.search_one(stac_request)

# get the Geotiff asset from the assets map
asset = utils.get_asset(stac_item, asset_type=enum.AssetType.GEOTIFF)

with tempfile.TemporaryDirectory() as d:
    file_path = utils.download_asset(asset=asset, save_directory=d)
    print("{0} has {1} bytes".format(os.path.basename(file_path), os.path.getsize(file_path)))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    20190826T190001Z_761_POM1_ST2_P.tif has 131373291 bytes
```


</details>



### Handling Deadlines
The `search` method is a gRPC streaming request. It sends a single request to the server and then maintains an open connection to the server, which then pushes results to the client. This means that if you have a long running sub-routine that executes between each iterated result from `search` you may exceed the 15 second timeout. If you have a stac request so large that the results create a memory problem or the blocking behavior limits your application performance, then you will want to use `offset` and `limit` as described in [AdvancedExamples.md](./AdvancedExamples.md#limits-and-offsets).

Otherwise, an easy way to iterate through results without timing-out on long running sub-routines is to capture the `search` results in a `list`.

For example:





<details><summary>Expand Python Code Sample</summary>


```python
import os
import tempfile
from datetime import date
from nsl.stac import StacRequest, GeometryData, ProjectionData, enum
from nsl.stac.utils import download_asset, get_asset, pb_timestampfield
from nsl.stac.client import NSLClient


ut_stadium_wkt = "POINT(-97.7323317 30.2830764)"
geometry_data = GeometryData(wkt=ut_stadium_wkt, proj=ProjectionData(epsg=4326))

# Query data from before September 1, 2019
time_filter = pb_timestampfield(value=date(2019, 9, 1), rel_type=enum.FilterRelationship.LTE)

# limit is set to 2 here, but it would work if you set it to 100 or 1000
stac_request = StacRequest(datetime=time_filter, intersects=geometry_data, limit=2)

# get a client interface to the gRPC channel. This client singleton is threadsafe
client = NSLClient()

# collect all stac items in a list
stac_items = list(client.search(stac_request))

with tempfile.TemporaryDirectory() as d:
    for stac_item in stac_items:
        print("STAC item id: {}".format(stac_item.id))
        asset = get_asset(stac_item, asset_type=enum.AssetType.GEOTIFF)
        filename = download_asset(asset=asset, save_directory=d)
        print("saved {}".format(os.path.basename(filename)))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC item id: 20190826T190001Z_761_POM1_ST2_P
    saved 20190826T190001Z_761_POM1_ST2_P.tif
    STAC item id: 20190826T185933Z_747_POM1_ST2_P
    saved 20190826T185933Z_747_POM1_ST2_P.tif
```


</details>



## Differences between gRPC+Protobuf STAC and OpenAPI+JSON STAC
If you are already familiar with STAC, you'll need to know that gRPC + Protobuf STAC is slightly different from the JSON definitions. 

JSON is naturally a flexible format and with linters you can force it to adhere to rules. Protobuf is a strict data format and that required a few differences between the JSON STAC specification and the protobuf specification:

### JSON STAC Compared with Protobuf STAC

#### STAC Item Comparison
For Comparison, here is the [JSON STAC item field summary](https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md#item-fields) and the [Protobuf STAC item field summary](https://geo-grpc.github.io/api/#epl.protobuf.v1.StacItem). Below is a table comparing the two:


| Field Name | STAC Protobuf Type                                                                                                       | STAC JSON Type                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| id         | [string](https://geo-grpc.github.io/api/#string)                                                                         | string                                                                     |
| type       | NA                                                                                                                       | string                                                                     |
| geometry   | [GeometryData](https://geo-grpc.github.io/api/#epl.protobuf.v1.GeometryData)                                             | [GeoJSON Geometry Object](https://tools.ietf.org/html/rfc7946#section-3.1) |
| bbox       | [EnvelopeData](https://geo-grpc.github.io/api/#epl.protobuf.v1.EnvelopeData)                                             | [number]                                                                   |
| properties | [google.protobuf.Any](https://developers.google.com/protocol-buffers/docs/proto3#any)                                    | Properties Object                                                          |
| links      | NA                                                                                                                       | [Link Object]                                                              |
| assets     | [StacItem.AssetsEntry](https://geo-grpc.github.io/api/#epl.protobuf.v1.StacItem.AssetsEntry)                             | Map                                                                        |
| collection | [string](https://geo-grpc.github.io/api/#string)                                                                         | string                                                                     |
| title      | [string](https://geo-grpc.github.io/api/#string)                                                                         | Inside Properties                                                          |
| datetime   | [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) | Inside Properties                                                          |
| observed   | [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) | Inside Properties                                                          |
| processed  | [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) | Inside Properties                                                          |
| updated    | [google.protobuf.Timestamp](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) | Inside Properties                                                          |
| duration   | [google.protobuf.Duration](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/duration.proto)   | Inside Properties                                                          |
| eo         | [Eo](https://geo-grpc.github.io/api/#epl.protobuf.v1.Eo)                                                                 | Inside Properties                                                          |
| sar        | [Sar](https://geo-grpc.github.io/api/#epl.protobuf.v1.Sar)                                                               | Inside Properties                                                          |
| landsat    | [Landsat](https://geo-grpc.github.io/api/#epl.protobuf.v1.Landsat)                                                       | Inside Properties                                                          |



#### Eo Comparison
For Comparison, here is the [JSON STAC Electro Optical field summary](https://github.com/radiantearth/stac-spec/tree/master/extensions/eo#item-fields) and the [Protobuf STAC Electro Optical field summary](https://geo-grpc.github.io/api/#epl.protobuf.v1.Eo). Below is a table comparing the two:

| JSON Field Name | JSON Data Type                                                                                 | Protobuf Field Name | Protobuf Data Type                                                                                                                |
| --------------- | ---------------------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| eo:bands        | [Band Object](https://github.com/radiantearth/stac-spec/tree/master/extensions/eo#band-object) | bands               | [Eo.Band](https://geo-grpc.github.io/api/#epl.protobuf.v1.Eo.Band)                                                                |
| eo:cloud_cover  | number                                                                                         | cloud_cover         | [google.protobuf.wrappers.FloatValue](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/wrappers.proto) |



### Updating the samples in this README
Use this README.ipynb notebook to update the README.md. Do not directly edit the README.md. It will be overwritten by output from `ipynb2md.py`. `ipynb2md.py` can be downloaded from this [gist](https://gist.github.com/davidraleigh/a24f637ccb018610a87aaacb12281452).

```bash
curl -o ipynb2md.py https://gist.githubusercontent.com/davidraleigh/a24f637ccb018610a87aaacb12281452/raw/009a50f29b920c7b00dcd4142c51bf6bf3c0cb3b/ipynb2md.py
```

Make your edits to the README.ipynb, in *Kernel->Restart & Run All* to confirm your changes worked, Save and Checkpoint, then run the python script `python ipynb2md.py -i README.ipynb`.

