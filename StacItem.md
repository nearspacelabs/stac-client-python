## STAC Item Properties
A STAC item is a metadata container for spatially and temporally bounded earth observation data. The data can be aerial imagery, radar data or other types of earth observation data. A STAC item has metadata properties describing the dataset and `Assets` that contain information for downloading the data being described. Almost all properties of a STAC item are aspects you can query by using a `StacRequest` with different types of filters.

Return to [README.md](./README.md)





<details><summary>Expand Python Code Sample</summary>


```python
from nsl.stac.client import NSLClient
from epl.protobuf.stac_pb2 import StacRequest

stac_request = StacRequest(id='20191110T005417Z_1594_ST2_POM1')

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
    id: "20191110T005417Z_1594_ST2_POM1"
    geometry {
      wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\316\252\210\342\367nX\300\265K\302O\323?>@\246\336\241u\325mX\300\211\271\345\000\310?>@:\337\320\324\322mX\300\251;N.\360B>@\343@\000K\365nX\300+\205\227~\373B>@\316\252\210\342\367nX\300\265K\302O\323?>@"
      sr {
        wkid: 4326
      }
      simple: STRONG_SIMPLE
    }
    bbox {
      xmin: -97.73387969347388
      ymin: 30.24914556129946
      xmax: -97.71599312207846
      ymax: 30.261650001518472
      sr {
        wkid: 4326
      }
    }
    properties {
      type_url: "type.googleapis.com/st.protobuf.SwiftMetadata"
      value: "\n\03420190829T153004Z_HAYS_COUNTY\022 4720b2613dc9377a70e74076acb739cf\032\02620191110T005320Z_DAVID \01022\032+POINT(-97.71175384521484 30.19917869567871):\003\010\346!:\005\rf\001\242FB|\n\013\010\331\226\240\353\005\020\320\357\343{\020\001 \272\014-kl\303\3025\353\227\361A=f\001\242FEfp\303\302M\235 \362AU\000\000HCZ$\032Gj?\360\3061\276\215F\272>/\263Z>1hy?\027\036\224\275\261\014\257\276\214W\023>\177\274m?b$\317\223l?\205\3413\276\313\270\255>F\256K>?\272z?\345\022\016\2756\006\247\276\206\335\313=Z\246p?R\03620190904T154946Z_1594_POM2_ST1Z\03620190829T172857Z_1594_POM1_ST2Z\03620190904T154533Z_1594_POM2_ST1Z\03620190904T154946Z_1594_POM2_ST1b\03620190829T172857Z_1594_POM1_ST2h\001p\001\200\001\304Y\210\001\220\373\023"
    }
    assets {
      key: "GEOTIFF_RGB"
      value {
        href: "https://swiftera-processed-data.storage.googleapis.com/20191110T005320Z_DAVID/Publish_0/20191110T005417Z_1594_ST2_POM1.tif"
        type: "image/vnd.stac.geotiff"
        eo_bands: RGB
        asset_type: GEOTIFF
        cloud_platform: GCP
        bucket_manager: "Swiftera"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20191110T005320Z_DAVID/Publish_0/20191110T005417Z_1594_ST2_POM1.tif"
      }
    }
    assets {
      key: "THUMBNAIL_RGB"
      value {
        href: "https://swiftera-processed-data.storage.googleapis.com/20191110T005320Z_DAVID/Publish_0/20191110T005417Z_1594_ST2_POM1_thumb.jpg"
        type: "image/jpeg"
        eo_bands: RGB
        asset_type: THUMBNAIL
        cloud_platform: GCP
        bucket_manager: "Swiftera"
        bucket_region: "us-central1"
        bucket: "swiftera-processed-data"
        object_path: "20191110T005320Z_DAVID/Publish_0/20191110T005417Z_1594_ST2_POM1_thumb.jpg"
      }
    }
    datetime {
      seconds: 1567099737
      nanos: 259586000
    }
    observed {
      seconds: 1567099737
      nanos: 259586000
    }
    processed {
      seconds: 1573347257
      nanos: 71578000
    }
    updated {
      seconds: 1573347266
      nanos: 103065000
    }
    eo {
      platform: SWIFT_2
      instrument: POM_1
      constellation: SWIFT
      sun_azimuth {
        value: 141.74072265625
      }
      sun_elevation {
        value: 64.46234130859375
      }
      off_nadir {
        value: 19.908658981323242
      }
      azimuth {
        value: 102.08956146240234
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
    STAC Item id: 20191110T005417Z_1594_ST2_POM1
    
    STAC Item observed: seconds: 1567099737
    nanos: 259586000
    
    STAC Item datetime: seconds: 1567099737
    nanos: 259586000
    
    STAC Item bbox: xmin: -97.73387969347388
    ymin: 30.24914556129946
    xmax: -97.71599312207846
    ymax: 30.261650001518472
    sr {
      wkid: 4326
    }
    
    STAC Item geometry: wkb: "\001\006\000\000\000\001\000\000\000\001\003\000\000\000\001\000\000\000\005\000\000\000\316\252\210\342\367nX\300\265K\302O\323?>@\246\336\241u\325mX\300\211\271\345\000\310?>@:\337\320\324\322mX\300\251;N.\360B>@\343@\000K\365nX\300+\205\227~\373B>@\316\252\210\342\367nX\300\265K\302O\323?>@"
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
    UTC Observed Scene: 2019-08-29 17:28:57
    UTC Processed Data: 2019-11-10 00:54:17
    UTC Updated Metadata: 2019-11-10 00:54:26
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
    MULTIPOLYGON (((-97.73387969347388 30.24931810849712, -97.71615353400793 30.24914556129946, -97.71599312207846 30.26147736940371, -97.73372149491074 30.26165000151847, -97.73387969347388 30.24931810849712)))
    
    centroid of polygon:
    POINT (-97.72493696704974 30.25539788861046)
    
    bounds:
    POLYGON ((-97.73387969347388 30.24914556129946, -97.73387969347388 30.26165000151847, -97.71599312207846 30.26165000151847, -97.71599312207846 30.24914556129946, -97.73387969347388 30.24914556129946))
    
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
    href: https://swiftera-processed-data.storage.googleapis.com/20191110T005320Z_DAVID/Publish_0/20191110T005417Z_1594_ST2_POM1.tif
    type: image/vnd.stac.geotiff
    protobuf enum number and name: 2, GEOTIFF
    
    THUMBNAIL_RGB asset key
    href: https://swiftera-processed-data.storage.googleapis.com/20191110T005320Z_DAVID/Publish_0/20191110T005417Z_1594_ST2_POM1_thumb.jpg
    type: image/jpeg
    protobuf enum number and name: 9, THUMBNAIL
    
```


</details>



As you can see above, our data only consists of jpg thumbnails and Geotiffs. But there can be other data stored in Assets in the future.

You can read more details about Assets [here](https://geo-grpc.github.io/api/#epl.protobuf.Asset)

### Electo Optical
Some imagery analysis tools require knowing certain types of electro optical information. Here's a printout of the information we've collected with data.





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
      value: 141.74072265625
    }
    sun_elevation {
      value: 64.46234130859375
    }
    off_nadir {
      value: 19.908658981323242
    }
    azimuth {
      value: 102.08956146240234
    }
    
```


</details>



The `platform` is the model of the vehicle holding the sensor. The `instrument` is the sensor the collected the scenes. In our case we're using `constellation` to represent a class of flight vehicles that we're flying. In the case of the Landsat satellite program the breakdown would be:

- `platform`: LANDSAT_8
- `sensor`: OLI_TIRS
- `constellation`: LANDSAT

These `sun_azimuth`, `sun_elevation`, `off_nadir` and `azimuth` are all boxed in the [google.protobuf.FloatValue type](https://developers.google.com/protocol-buffers/docs/reference/csharp/class/google/protobuf/well-known-types/float-value). To get at the value you must access the `value` field:





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
    sun_azimuth: 141.74072
    sun_elevation: 64.46234
    off_nadir: 19.90866
    azimuth: 102.08956
```


</details>



Notice that we're only printing out 5 decimal places. As these are stored as float values, we can't trust any of the precision that Python provides us beyond what we know the data to possess.

You can read more details about electro-optical data [here](https://geo-grpc.github.io/api/#epl.protobuf.Eo)

Return to [README.md](./README.md)
