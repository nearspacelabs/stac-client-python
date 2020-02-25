## STAC Item Properties
A STAC item is a metadata container for spatially and temporally bounded earth observation data. The data can be aerial imagery, radar data or other types of earth observation data. A STAC item has metadata properties describing the dataset and `Assets` that contain information for downloading the data being described. Almost all properties of a STAC item are aspects you can query by using a `StacRequest` with different types of filters.

Return to [README.md](./README.md)





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.client import NSLClient
from nsl.stac import StacRequest

stac_request = StacRequest(id='20190829T173429Z_1759_POM1_ST2_P')

# get a client interface to the gRPC channel
client = NSLClient()
# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    nsl client connecting to stac service at: api.nearspacelabs.net:9090
    
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
    id: "20190829T173429Z_1759_POM1_ST2_P"
    geometry {
      wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\205N\247\203gqX\300l\226EM\267\037>@L\034efdqX\300q\307\267}L\">@\364y\rlxrX\300\030\316j\2561\">@?\305aT\177rX\300\322\244_\330\210\037>@\205N\247\203gqX\300l\226EM\267\037>@"
      sr {
        wkid: 4326
      }
      simple: STRONG_SIMPLE
    }
    bbox {
      xmin: -97.78902158306026
      ymin: 30.123181842184586
      xmax: -97.77175292848659
      ymax: 30.133979661338746
      sr {
        wkid: 4326
      }
    }
    properties {
      type_url: "type.googleapis.com/st.protobuf.SwiftMetadata"
      value: "\n\03420190829T153004Z_HAYS_COUNTY\022 0495ead38e491e637414d508f2d230d6\032\03120200225T182845Z_SWIFTERA \010B\003 \337\rR\03620191202T150234Z_1759_ST2_POM1Z\03620190829T173429Z_1759_POM1_ST2Z\03620191122T065203Z_1759_ST2_POM1Z\03620191122T065513Z_1759_ST2_POM1Z\03620191202T150234Z_1759_ST2_POM1b\03620190829T173429Z_1759_POM1_ST2h\001p\001x\325\020\200\001\340\014\210\001\265\035\250\001\200\020"
    }
    assets {
      key: "GEOTIFF_RGB"
      value {
        href: "https://eap.nearspacelabs.net/download/20200225T182845Z_SWIFTERA/Publish_0/20191202T150234Z_1759_ST2_POM1_P.tif"
        type: "image/vnd.stac.geotiff"
        eo_bands: RGB
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Near Space Labs"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20200225T182845Z_SWIFTERA/Publish_0/20191202T150234Z_1759_ST2_POM1_P.tif"
      }
    }
    assets {
      key: "THUMBNAIL_RGB"
      value {
        href: "https://eap.nearspacelabs.net/download/20200225T182845Z_SWIFTERA/Publish_0/20191202T150234Z_1759_ST2_POM1_P_thumb.jpg"
        type: "image/jpeg"
        eo_bands: RGB
        asset_type: THUMBNAIL
        cloud_platform: GCP
        bucket_manager: "Near Space Labs"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20200225T182845Z_SWIFTERA/Publish_0/20191202T150234Z_1759_ST2_POM1_P_thumb.jpg"
      }
    }
    datetime {
      seconds: 1567100069
      nanos: 429146000
    }
    observed {
      seconds: 1567100069
      nanos: 429146000
    }
    processed {
      seconds: 1582655391
      nanos: 944032000
    }
    updated {
      seconds: 1582655395
      nanos: 410392398
    }
    eo {
      platform: SWIFT_2
      instrument: POM_1
      constellation: SWIFT
      sun_azimuth {
        value: 144.40382385253906
      }
      sun_elevation {
        value: 65.16360473632812
      }
      gsd {
        value: 0.30000001192092896
      }
      off_nadir {
        value: 21.890628814697266
      }
      azimuth {
        value: -155.82078552246094
      }
      sr {
        wkid: 32614
      }
    }
    
```


</details>



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
    STAC Item id: 20190829T173429Z_1759_POM1_ST2_P
    
    STAC Item observed: seconds: 1567100069
    nanos: 429146000
    
    STAC Item datetime: seconds: 1567100069
    nanos: 429146000
    
    STAC Item bbox: xmin: -97.78902158306026
    ymin: 30.123181842184586
    xmax: -97.77175292848659
    ymax: 30.133979661338746
    sr {
      wkid: 4326
    }
    
    STAC Item geometry: wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\205N\247\203gqX\300l\226EM\267\037>@L\034efdqX\300q\307\267}L\">@\364y\rlxrX\300\030\316j\2561\">@?\305aT\177rX\300\322\244_\330\210\037>@\205N\247\203gqX\300l\226EM\267\037>@"
    sr {
      wkid: 4326
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
print("UTC Processed Data: {}".format(datetime.utcfromtimestamp(stac_item.processed.seconds)))
print("UTC Updated Metadata: {}".format(datetime.utcfromtimestamp(stac_item.updated.seconds)))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    UTC Observed Scene: 2019-08-29 17:34:29
    UTC Processed Data: 2020-02-25 18:29:51
    UTC Updated Metadata: 2020-02-25 18:29:55
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
    MULTIPOLYGON (((-97.77194300974413 30.12389071415821, -97.77175292848659 30.13397966133875, -97.7885999805074 30.13357057673974, -97.78902158306026 30.12318184218459, -97.77194300974413 30.12389071415821)))
    
    centroid of polygon:
    POINT (-97.78037008507624 30.12864316190825)
    
    bounds:
    POLYGON ((-97.78902158306026 30.12318184218459, -97.78902158306026 30.13397966133875, -97.77175292848659 30.13397966133875, -97.77175292848659 30.12318184218459, -97.78902158306026 30.12318184218459))
    
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
     href: https://eap.nearspacelabs.net/download/20200225T182845Z_SWIFTERA/Publish_0/20191202T150234Z_1759_ST2_POM1_P_thumb.jpg
     type: image/jpeg
     protobuf enum number and name: 9, THUMBNAIL
    
    GEOTIFF
     href: https://eap.nearspacelabs.net/download/20200225T182845Z_SWIFTERA/Publish_0/20191202T150234Z_1759_ST2_POM1_P.tif
     type: image/vnd.stac.geotiff
     protobuf enum number and name: 2, GEOTIFF
    
```


</details>



As you can see above, our data only consists of jpg thumbnails and Geotiffs. But there can be other data stored in Assets in the future.

You can read more details about Assets [here](https://geo-grpc.github.io/api/#epl.protobuf.Asset)

### Electo Optical
Some imagery analysis tools require knowing certain types of electro optical information. Here's a printout of the information we've collected with data. A summary of Electro Optical values can be found [here](https://geo-grpc.github.io/api/#epl.protobuf.Eo).





<details><summary>Expand Python Code Sample</summary>


```python
print(stac_item.eo)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    platform: SWIFT_2
    instrument: POM_1
    constellation: SWIFT
    sun_azimuth {
      value: 144.40382385253906
    }
    sun_elevation {
      value: 65.16360473632812
    }
    gsd {
      value: 0.30000001192092896
    }
    off_nadir {
      value: 21.890628814697266
    }
    azimuth {
      value: -155.82078552246094
    }
    sr {
      wkid: 32614
    }
    
```


</details>



The `platform` is the model of the vehicle holding the sensor. The `instrument` is the sensor the collected the scenes. In our case we're using `constellation` to represent a class of flight vehicles that we're flying. In the case of the Landsat satellite program the breakdown would be:

- `platform`: LANDSAT_8
- `sensor`: OLI_TIRS
- `constellation`: LANDSAT

These `sun_azimuth`, `sun_elevation`, `off_nadir` and `azimuth` are all boxed in the [google.protobuf.FloatValue type](https://developers.google.com/protocol-buffers/docs/reference/csharp/class/google/protobuf/well-known-types/float-value). To get at the value you must access the `value` field.





<details><summary>Expand Python Code Sample</summary>


```python
print("sun_azimuth: {:.5f}".format(stac_item.eo.sun_azimuth.value))
print("sun_elevation: {:.5f}".format(stac_item.eo.sun_elevation.value))
print("off_nadir: {:.5f}".format(stac_item.eo.off_nadir.value))
print("azimuth: {:.5f}".format(stac_item.eo.azimuth.value))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    sun_azimuth: 144.40382
    sun_elevation: 65.16360
    off_nadir: 21.89063
    azimuth: -155.82079
```


</details>



Notice that we're only printing out 5 decimal places. As these are stored as float values, we can't trust any of the precision that Python provides us beyond what we know the data to possess.

You can read more details about electro-optical data [here](https://geo-grpc.github.io/api/#epl.protobuf.Eo)

Return to [README.md](./README.md)
