
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
    nsl client connecting to stac service at: eap.nearspacelabs.net:9090
    
    Stac item id 20191122T130410Z_640_ST2_POM1, date, 2019-04-12T12:16:02+00:00, is before 2019-08-20T00:00:00+00:00:True
    Stac item id 20191122T130408Z_641_ST2_POM1, date, 2019-04-12T12:16:15+00:00, is before 2019-08-20T00:00:00+00:00:True
```


</details>


