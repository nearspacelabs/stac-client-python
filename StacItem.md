## STAC Item Properties
A STAC item is a metadata container for spatially and temporally bounded earth observation data. The data can be aerial imagery, radar data or other types of earth observation data. A STAC item has metadata properties describing the dataset and `Assets` that contain information for downloading the data being described. Almost all properties of a STAC item are aspects you can query by using a `StacRequest` with different types of filters.

Return to [README.md](./README.md)





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest

stac_request = StacRequest(id='20190826T185828Z_715_POM1_ST2_P')

# get a client interface to the gRPC channel
client = NSLClient()
# for this request we might as well use the search one, as STAC ids ought to be unique
stac_item = client.search_one(stac_request)
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    nsl client connecting to stac service at: eap.nearspacelabs.net:9090
    
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
    id: "20190826T185828Z_715_POM1_ST2_P"
    geometry {
      wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\367\330\320\314\025nX\300\031\2774\223vC>@3\312/\034-nX\300a\326Z\371*F>@\265\023\016i@oX\300\355\303\030N\350E>@\315\272\247\322.oX\300u\036\372\212)C>@\367\330\320\314\025nX\300\031\2774\223vC>@"
      sr {
        wkid: 4326
      }
      simple: STRONG_SIMPLE
    }
    bbox {
      xmin: -97.73830629706102
      ymin: 30.262352644027903
      xmax: -97.7200805701758
      ymax: 30.27409323184691
      sr {
        wkid: 4326
      }
    }
    properties {
      type_url: "type.googleapis.com/st.protobuf.SwiftMetadata"
      value: "\n\03620190826T163847Z_TRAVIS_COUNTY\022 0495ead38e491e637414d508f2d230d6\032\03120191203T045008Z_SWIFTERA \0102.\032\'POINT(-97.75460815429688 30.3447265625):\003\010\346!:\005\r\232\266\244FB\003 \313\005R\03520191202T145554Z_715_ST2_POM1Z\03520190826T185828Z_715_POM1_ST2Z\03520191122T061353Z_715_ST2_POM1Z\03520191122T061722Z_715_ST2_POM1Z\03520191202T145554Z_715_ST2_POM1b\03520190826T185828Z_715_POM1_ST2h\001p\001x\326\001\200\001\262*\210\001\276\203\022"
    }
    assets {
      key: "GEOTIFF_RGB"
      value {
        href: "https://eap.nearspacelabs.net/download/20191203T045008Z_SWIFTERA/Publish_0/20190826T185828Z_715_POM1_ST2_P.tif"
        type: "image/vnd.stac.geotiff"
        eo_bands: RGB
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Swiftera"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20191203T045008Z_SWIFTERA/Publish_0/20190826T185828Z_715_POM1_ST2_P.tif"
      }
    }
    assets {
      key: "THUMBNAIL_RGB"
      value {
        href: "https://eap.nearspacelabs.net/download/20191203T045008Z_SWIFTERA/Publish_0/20190826T185828Z_715_POM1_ST2_P_thumb.jpg"
        type: "image/jpeg"
        eo_bands: RGB
        asset_type: THUMBNAIL
        cloud_platform: GCP
        bucket_manager: "Swiftera"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20191203T045008Z_SWIFTERA/Publish_0/20190826T185828Z_715_POM1_ST2_P_thumb.jpg"
      }
    }
    datetime {
      seconds: 1566845908
      nanos: 632167000
    }
    observed {
      seconds: 1566845908
      nanos: 632167000
    }
    processed {
      seconds: 1575352682
      nanos: 861234000
    }
    updated {
      seconds: 1575352687
      nanos: 268198954
    }
    eo {
      platform: SWIFT_2
      instrument: POM_1
      constellation: SWIFT
      sun_azimuth {
        value: 197.96905517578125
      }
      sun_elevation {
        value: 69.09848022460938
      }
      gsd {
        value: 0.30000001192092896
      }
      off_nadir {
        value: 22.70497703552246
      }
      azimuth {
        value: 163.9722137451172
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
    STAC Item id: 20190826T185828Z_715_POM1_ST2_P
    
    STAC Item observed: seconds: 1566845908
    nanos: 632167000
    
    STAC Item datetime: seconds: 1566845908
    nanos: 632167000
    
    STAC Item bbox: xmin: -97.73830629706102
    ymin: 30.262352644027903
    xmax: -97.7200805701758
    ymax: 30.27409323184691
    sr {
      wkid: 4326
    }
    
    STAC Item geometry: wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\367\330\320\314\025nX\300\031\2774\223vC>@3\312/\034-nX\300a\326Z\371*F>@\265\023\016i@oX\300\355\303\030N\350E>@\315\272\247\322.oX\300u\036\372\212)C>@\367\330\320\314\025nX\300\031\2774\223vC>@"
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
    UTC Observed Scene: 2019-08-26 18:58:28
    UTC Processed Data: 2019-12-03 05:58:02
    UTC Updated Metadata: 2019-12-03 05:58:07
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
    MULTIPOLYGON (((-97.7200805701758 30.26352806127315, -97.72150330225922 30.27409323184691, -97.73830629706102 30.27307594399092, -97.73723284129956 30.2623526440279, -97.7200805701758 30.26352806127315)))
    
    centroid of polygon:
    POINT (-97.72929640107934 30.26824224262507)
    
    bounds:
    POLYGON ((-97.73830629706102 30.2623526440279, -97.73830629706102 30.27409323184691, -97.7200805701758 30.27409323184691, -97.7200805701758 30.2623526440279, -97.73830629706102 30.2623526440279))
    
```


</details>



### Assets
Each STAC item should have at least one asset. An asset should be all the information you'll need to download the asset in question. For Near Space Labs customers, you'll be using the href, but you can also see the private bucket details of the asset. In protobuf the asset map has a key for each asset available. There's no part of the STAC specification for defining key names. Near Space Labs typically uses the data type, the optical bands and the cloud storage provider to construct a key name.





<details><summary>Expand Python Code Sample</summary>


```python
from epl.protobuf.stac_pb2 import AssetType
for asset_key in stac_item.assets:
    print("{} asset key".format(asset_key))
    asset = stac_item.assets[asset_key]
    print("href: {}".format(asset.href))
    print("type: {}".format(asset.type))
    print("protobuf enum number and name: {0}, {1}\n".format(asset.asset_type, AssetType.Name(asset.asset_type)))
```


</details>




<details><summary>Expand Python Print-out</summary>


```text
    GEOTIFF_RGB asset key
    href: https://eap.nearspacelabs.net/download/20191203T045008Z_SWIFTERA/Publish_0/20190826T185828Z_715_POM1_ST2_P.tif
    type: image/vnd.stac.geotiff
    protobuf enum number and name: 2, GEOTIFF
    
    THUMBNAIL_RGB asset key
    href: https://eap.nearspacelabs.net/download/20191203T045008Z_SWIFTERA/Publish_0/20190826T185828Z_715_POM1_ST2_P_thumb.jpg
    type: image/jpeg
    protobuf enum number and name: 9, THUMBNAIL
    
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
      value: 197.96905517578125
    }
    sun_elevation {
      value: 69.09848022460938
    }
    gsd {
      value: 0.30000001192092896
    }
    off_nadir {
      value: 22.70497703552246
    }
    azimuth {
      value: 163.9722137451172
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
    sun_azimuth: 197.96906
    sun_elevation: 69.09848
    off_nadir: 22.70498
    azimuth: 163.97221
```


</details>



Notice that we're only printing out 5 decimal places. As these are stored as float values, we can't trust any of the precision that Python provides us beyond what we know the data to possess.

You can read more details about electro-optical data [here](https://geo-grpc.github.io/api/#epl.protobuf.Eo)

Return to [README.md](./README.md)
