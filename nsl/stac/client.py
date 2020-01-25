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

from epl.protobuf import stac_pb2

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

    def update_service_url(self, stac_service_url):
        """
        update the stac service address
        :param stac_service_url: localhost:8080, 34.34.34.34:9000, http://api.nearspacelabs.net:9090, etc
        :return:
        """
        self._stac_service.update_service_url(stac_service_url=stac_service_url)

    def insert_one(self, stac_item: stac_pb2.StacItem, timeout=15) -> stac_pb2.StacDbResponse:
        """
        Insert on item into the stac service
        :param timeout: timeout for request
        :param stac_item: item to insert
        :return: StacDbResponse, the response of the success of the insert
        """
        return self._stac_service.stub.InsertOne(stac_item, timeout=timeout, metadata=(
            ('authorization', bearer_auth.auth_header()),
        ))

    def search_one(self, stac_request: stac_pb2.StacRequest, timeout=15) -> stac_pb2.StacItem:
        """
        search for one item from the db that matches the stac request
        :param timeout: timeout for request
        :param stac_request: StacRequest of query parameters to filter by
        :return: StacItem
        """
        # limit to only search Near Space Labs SWIFT data
        if self._nsl_only:
            stac_request.eo.MergeFrom(stac_pb2.EoRequest(constellation=stac_pb2.Eo.SWIFT))

        return self._stac_service.stub.SearchOne(stac_request, timeout=timeout, metadata=(
            ('authorization', bearer_auth.auth_header()),
        ))

    def count(self, stac_request: stac_pb2.StacRequest, timeout=15) -> int:
        """
        count all the items in the database that match the stac request
        :param timeout: timeout for request
        :param stac_request: StacRequest query parameters to apply to count method (limit ignored)
        :return: int
        """
        # limit to only search Near Space Labs SWIFT data
        if self._nsl_only:
            stac_request.eo.MergeFrom(stac_pb2.EoRequest(constellation=stac_pb2.Eo.SWIFT))

        db_result = self._stac_service.stub.Count(stac_request, timeout=timeout, metadata=(
            ('authorization', bearer_auth.auth_header()),
        ))
        return db_result.count

    def search(self, stac_request: stac_pb2.StacRequest, timeout=15) -> Iterator[stac_pb2.StacItem]:
        """
        search for stac items by using StacRequest. return a stream of StacItems
        :param timeout: timeout for request
        :param stac_request: StacRequest of query parameters to filter by
        :return: stream of StacItems
        """
        # limit to only search Near Space Labs SWIFT data
        if self._nsl_only:
            stac_request.eo.MergeFrom(stac_pb2.EoRequest(constellation=stac_pb2.Eo.SWIFT))

        results_generator = self._stac_service.stub.Search(stac_request, timeout=timeout, metadata=(
            ('authorization', bearer_auth.auth_header()),
        ))
        return results_generator
