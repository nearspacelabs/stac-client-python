# gRPC stac-client-python
#### A gRPC Spatio Temporal Asset Catalog python client 
This python client library is used for conneting to a gRPC enabled STAC service. 

Defining STAC from https://stacspec.org/:
> The SpatioTemporal Asset Catalog (STAC) specification provides a common language to describe a range of geospatial information, so it can more easily be indexed and discovered.  A 'spatiotemporal asset' is any file that represents information about the earth captured in a certain space and time.

Defining gRPC from https://grpc.io
> INSERT GRPC overview here

way for storing Spatio temporal asset information and make it searchable, by spatial query, time query and other data aspects. 

### Environment Variables
There are a few environment variables that the stac-client-python library relies on for accessing the STAC service:

- STAC_SERVICE, the address of the stac service you connect to (defaults to "localhost:10000")
- AUTH
- BEARER

### StacItem
The STAC item for a specific observation of data is summarized in the [stac repo](github.com/radiantearth/stac-spec/item-spec/README.md).

is represented by a protobuf message in the stac client.  

#### Google DataTypes vs native data types
   - TimeStamp
   - FloatValue

### StacRequest
   - 