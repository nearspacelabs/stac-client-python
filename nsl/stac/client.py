# Copyright 2019-20 Near Space Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# for additional information, contact:
#   info@nearspacelabs.com

from typing import Iterator

from epl.protobuf.v1 import stac_pb2

from nsl.stac import stac_service as stac_singleton
from nsl.stac import bearer_auth


class NSLClient:
    def __init__(self, nsl_only=True):
        """
        Create a client connection to a gRPC STAC service. nsl_only limits all queries to only return data from Near
        Space Labs.
        :param nsl_only:
        """
        self._stac_service = stac_singleton
        self._nsl_only = nsl_only

    @property
    def default_nsl_id(self):
        """
if you don't set the nsl_id for each stac request, then this nsl_id is the default choice. if you set this default
value you must make sure that the nsl_id has already been 'set' by calling `set_credentials`
        :return:
        """
        return bearer_auth.default_nsl_id

    def set_credentials(self, nsl_id: str, nsl_secret: str):
        """
Set nsl_id and secret for use in querying metadata and downloading imagery
        :param nsl_id:
        :param nsl_secret:
        """
        bearer_auth.set_credentials(nsl_id=nsl_id, nsl_secret=nsl_secret)

    def update_service_url(self, stac_service_url):
        """
        update the stac service address
        :param stac_service_url: localhost:8080, 34.34.34.34:9000, http://api.nearspacelabs.net:9090, etc
        :return:
        """
        self._stac_service.update_service_url(stac_service_url=stac_service_url)

    def insert_one(self,
                   stac_item: stac_pb2.StacItem,
                   timeout=15,
                   nsl_id: str = None,
                   profile_name: str = None) -> stac_pb2.StacDbResponse:
        """
        Insert on item into the stac service
        :param nsl_id: ADVANCED ONLY. Only necessary if more than one nsl_id and nsl_secret have been defined with
        set_credentials method.  Specify nsl_id to use. if NSL_ID and NSL_SECRET environment variables not set must use
        NSLClient object's set_credentials to set credentials
        :param timeout: timeout for request
        :param stac_item: item to insert
        :param profile_name: if a ~/.nsl/credentials file exists, you can override the [default] credential usage, by
        using a different profile name
        :return: StacDbResponse, the response of the success of the insert
        """
        metadata = (('authorization', bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)),)
        return self._stac_service.stub.InsertOneItem(stac_item, timeout=timeout, metadata=metadata)

    def search_one(self,
                   stac_request: stac_pb2.StacRequest,
                   timeout=15,
                   nsl_id: str = None,
                   profile_name: str = None) -> stac_pb2.StacItem:
        """
        search for one item from the db that matches the stac request
        :param timeout: timeout for request
        :param stac_request: StacRequest of query parameters to filter by
        :param nsl_id: ADVANCED ONLY. Only necessary if more than one nsl_id and nsl_secret have been defined with
        set_credentials method.  Specify nsl_id to use. if NSL_ID and NSL_SECRET environment variables not set must use
        NSLClient object's set_credentials to set credentials
        :param profile_name: if a ~/.nsl/credentials file exists, you can override the [default] credential usage, by
        using a different profile name
        :return: StacItem
        """
        # limit to only search Near Space Labs SWIFT data
        if self._nsl_only:
            stac_request.mission_enum = stac_pb2.SWIFT

        metadata = (('authorization', bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)),)
        return self._stac_service.stub.SearchOneItem(stac_request, timeout=timeout, metadata=metadata)

    def count(self,
              stac_request: stac_pb2.StacRequest,
              timeout=15,
              nsl_id: str = None,
              profile_name: str = None) -> int:
        """
        count all the items in the database that match the stac request
        :param timeout: timeout for request
        :param stac_request: StacRequest query parameters to apply to count method (limit ignored)
        :param nsl_id: ADVANCED ONLY. Only necessary if more than one nsl_id and nsl_secret have been defined with
        set_credentials method.  Specify nsl_id to use. if NSL_ID and NSL_SECRET environment variables not set must use
        NSLClient object's set_credentials to set credentials
        :param profile_name: if a ~/.nsl/credentials file exists, you can override the [default] credential usage, by
        using a different profile name
        :return: int
        """
        # limit to only search Near Space Labs SWIFT data
        if self._nsl_only:
            stac_request.mission_enum = stac_pb2.SWIFT

        metadata = (('authorization', bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)),)
        db_result = self._stac_service.stub.CountItems(stac_request, timeout=timeout, metadata=metadata)
        return db_result.count

    def search(self,
               stac_request: stac_pb2.StacRequest,
               timeout=15,
               nsl_id: str = None,
               profile_name: str = None) -> Iterator[stac_pb2.StacItem]:
        """
        search for stac items by using StacRequest. return a stream of StacItems
        :param timeout: timeout for request
        :param stac_request: StacRequest of query parameters to filter by
        :param nsl_id: ADVANCED ONLY. Only necessary if more than one nsl_id and nsl_secret have been defined with
        set_credentials method.  Specify nsl_id to use. if NSL_ID and NSL_SECRET environment variables not set must use
        NSLClient object's set_credentials to set credentials
        :param profile_name: if a ~/.nsl/credentials file exists, you can override the [default] credential usage, by
        using a different profile name
        :return: stream of StacItems
        """
        # limit to only search Near Space Labs SWIFT data
        if self._nsl_only:
            stac_request.mission_enum = stac_pb2.SWIFT

        metadata = (('authorization', bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)),)
        results_generator = self._stac_service.stub.SearchItems(stac_request, timeout=timeout, metadata=metadata)
        return results_generator
