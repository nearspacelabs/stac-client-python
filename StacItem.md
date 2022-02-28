## STAC Item Properties
A STAC item is a metadata container for spatially and temporally bounded earth observation data. The data can be aerial imagery, radar data or other types of earth observation data. A STAC item has metadata properties describing the dataset and `Assets` that contain information for downloading the data being described. Almost all properties of a STAC item are aspects you can query by using a `StacRequest` with different types of filters.

Return to [README.md](./README.md)





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.client import NSLClient
from nsl.stac import StacRequest

stac_request = StacRequest(id='20190822T183518Z_746_POM1_ST2_P')

# get a client interface to the gRPC channel
client = NSLClient()
# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)
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
```


</details>



Here are the sections where we go into more detail about properties and assets.

- [ID, Temporal, and Spatial](#id-temporal-and-spatial)
- [Assets](#assets)
- [Electro Optical](#electro-optical)

Printing out all the data demonstrates what is typically in a StacItem:





<details><summary>Expand Python Code Sample</summary>


```python
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



In addition to spatial and temporal details there are also details about the capturing device. We use both strings (to stay compliant with STAC JSON) and enum fields for these details. The `platform_enum` and `platform` is the model of the vehicle holding the sensor. The `instrument_enum` and `instrument` is the sensor that collected the scenes. In our case we're using `mission_enum` and `mission` to represent a class of flight vehicles that we're flying. In the case of the Landsat satellite program the breakdown would be:

 *   `platform_enum`: `enum.PLATFORM.LANDSAT_8`
 *   `sensor_enum`: `enum.SENSOR.OLI_TIRS`
 *   `mission_enum`: `enum.MISSION.LANDSAT`
 *   `platform`: "LANDSAT_8"
 *   `sensor`: "OLI_TIRS"
 *   `mission`: "LANDSAT"


### ID Temporal and Spatial
Every STAC Item has a unique id, a datetime/observation, and a geometry/bbox (bounding-box).





<details><summary>Expand Python Code Sample</summary>


```python
print("STAC Item id: {}\n".format(stac_item.id))
print("STAC Item observed: {}".format(stac_item.observed))
print("STAC Item datetime: {}".format(stac_item.datetime))
print("STAC Item bbox: {}".format(stac_item.bbox))
print("STAC Item geometry: {}".format(stac_item.geometry))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    STAC Item id: 20190822T183518Z_746_POM1_ST2_P
    
    STAC Item observed: seconds: 1566498918
    nanos: 505476000
    
    STAC Item datetime: seconds: 1566498918
    nanos: 505476000
    
    STAC Item bbox: xmin: -97.7466867683867
    ymin: 30.278398961994966
    xmax: -97.72990596574927
    ymax: 30.288621181865743
    proj {
      epsg: 4326
    }
    
    STAC Item geometry: wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\352\244L\267\311oX\300\316\340\320\247\234I>@\241\273\2606\267oX\300<\002\205\'EG>@\031\003\203\307\266nX\3001z\244\372\233G>@CCAI\306nX\300\326\013\351\023\343I>@\352\244L\267\311oX\300\316\340\320\247\234I>@"
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
    
```


</details>



As you can see above, the `id` is a string value. The format of the id is typically not guessable (ours is based of off the time the data was processed, the image index, the platform and the sensor).

The `observed` and `datetime` fields are the same value. STAC specification uses a generic field `datetime` to define the spatial component, the `S`, in STAC. We wanted a more descriptive variable, so we use `observed`, as in, the moment the scene was captured. This is a UTC timestamp in seconds and nano seconds.

The `bbox` field describes the xmin, ymin, xmax, and ymax points that describe the bounding box that contains the scene. The `sr` field has an [epsg](http://www.epsg.org/) `wkid`. In this case the 4326 `wkid` indicates [WGS-84](http://epsg.io/4326)

The `geometry` field has subfields `wkb`, `sr`, and `simple`. The `wkb` is a [well known binary](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry#Well-known_binary) geometry format preferred for it's size. `sr` is the same as in the `bbox`. `simple` can be ignored.

Below we demonstrate how you can create python `datetime` objects:





<details><summary>Expand Python Code Sample</summary>


```python
from datetime import datetime
print("UTC Observed Scene: {}".format(datetime.utcfromtimestamp(stac_item.observed.seconds)))
print("UTC Processed Data: {}".format(datetime.utcfromtimestamp(stac_item.created.seconds)))
print("UTC Updated Metadata: {}".format(datetime.utcfromtimestamp(stac_item.updated.seconds)))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    UTC Observed Scene: 2019-08-22 18:35:18
    UTC Processed Data: 2020-08-06 19:56:51
    UTC Updated Metadata: 2021-02-01 15:28:06
```


</details>



Updated is when the metadata was last updated. Typically that will be right after it's `processed` timestamp.

Below is a demo of using shapely to get at the geometry data.





<details><summary>Expand Python Code Sample</summary>


```python
from shapely.geometry import Polygon
from shapely.wkb import loads

print("wkt printout of polygon:\n{}\n".format(loads(stac_item.geometry.wkb)))
print("centroid of polygon:\n{}\n".format(loads(stac_item.geometry.wkb).centroid))
print("bounds:\n{}\n".format(Polygon.from_bounds(stac_item.bbox.xmin, 
                                                 stac_item.bbox.ymin, 
                                                 stac_item.bbox.xmax, 
                                                 stac_item.bbox.ymax)))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    wkt printout of polygon:
    MULTIPOLYGON (((-97.7466867683867 30.28754662370266, -97.74555747279238 30.27839896199497, -97.72990596574927 30.27972380176124, -97.73085242627444 30.28862118186574, -97.7466867683867 30.28754662370266)))
    
    centroid of polygon:
    POINT (-97.738289581264 30.28357703330576)
    
    bounds:
    POLYGON ((-97.7466867683867 30.27839896199497, -97.7466867683867 30.28862118186574, -97.72990596574927 30.28862118186574, -97.72990596574927 30.27839896199497, -97.7466867683867 30.27839896199497))
    
```


</details>



### Assets
Each STAC item should have at least one asset. An asset should be all the information you'll need to download the asset in question. For Near Space Labs customers, you'll be using the href, but you can also see the private bucket details of the asset. In protobuf the asset map has a key for each asset available. There's no part of the STAC specification for defining key names. Near Space Labs typically uses the data type, the optical bands and the cloud storage provider to construct a key name.





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac import Asset, utils
from nsl.stac.enum import AssetType
def print_asset(asset: Asset):
    asset_name = AssetType(asset.asset_type).name
    print(" href: {}".format(asset.href))
    print(" type: {}".format(asset.type))
    print(" protobuf enum number and name: {0}, {1}".format(asset.asset_type, asset_name))
    print()

print("there are {} assets".format(len(stac_item.assets)))
print(AssetType.THUMBNAIL.name)
print_asset(utils.get_asset(stac_item, asset_type=AssetType.THUMBNAIL))

print(AssetType.GEOTIFF.name)
print_asset(utils.get_asset(stac_item, asset_type=AssetType.GEOTIFF))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    there are 2 assets
    THUMBNAIL
     href: https://api.nearspacelabs.net/download/20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.png
     type: image/png
     protobuf enum number and name: 9, THUMBNAIL
    
    GEOTIFF
     href: https://api.nearspacelabs.net/download/20190822T162258Z_TRAVIS_COUNTY/Published/REGION_0/20190822T183518Z_746_POM1_ST2_P.tif
     type: image/vnd.stac.geotiff
     protobuf enum number and name: 2, GEOTIFF
    
```


</details>



As you can see above, our data only consists of jpg thumbnails and Geotiffs. But there can be other data stored in Assets in the future.

You can read more details about Assets [here](https://geo-grpc.github.io/api/#epl.protobuf.Asset)

### View
Some imagery analysis tools require knowing certain types of angular information. Here's a printout of the information we've collected with data. A summary of View values can be found [here](https://geo-grpc.github.io/api/#epl.protobuf.v1.View).





<details><summary>Expand Python Code Sample</summary>


```python
print(stac_item.view)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
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
    
```


</details>



These `sun_azimuth`, `sun_elevation`, `off_nadir` and `azimuth` are all boxed in the [google.protobuf.FloatValue type](https://developers.google.com/protocol-buffers/docs/reference/csharp/class/google/protobuf/well-known-types/float-value). To get at the value you must access the `value` field.





<details><summary>Expand Python Code Sample</summary>


```python
print("sun_azimuth: {:.5f}".format(stac_item.view.sun_azimuth.value))
print("sun_elevation: {:.5f}".format(stac_item.view.sun_elevation.value))
print("off_nadir: {:.5f}".format(stac_item.view.off_nadir.value))
print("azimuth: {:.5f}".format(stac_item.view.azimuth.value))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    sun_azimuth: 181.26959
    sun_elevation: 71.41289
    off_nadir: 9.42327
    azimuth: -74.85271
```


</details>



Notice that we're only printing out 5 decimal places. As these are stored as float values, we can't trust any of the precision that Python provides us beyond what we know the data to possess.

You can read more details about electro-optical data [here](https://geo-grpc.github.io/api/#epl.protobuf.Eo)

Return to [README.md](./README.md)
