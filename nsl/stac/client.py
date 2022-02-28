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

import requests

from typing import Iterator, List
from warnings import warn

from epl.protobuf.v1 import stac_pb2

from nsl.stac import AUTH0_TENANT, bearer_auth, stac_service as stac_singleton, utils, TimestampFilter
from nsl.stac.destinations import BaseDestination, MemoryDestination
from nsl.stac.subscription import Subscription
from nsl.stac.utils import item_region


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
        if you don't set the nsl_id for each stac request, then this nsl_id is the default choice.
        if you set this default value you must make sure that the nsl_id has already been 'set' by calling `set_credentials`
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
        if db_result.status:
            # print db_result
            print(db_result.status)
        return db_result.count

    def search(self,
               stac_request: stac_pb2.StacRequest,
               timeout=15,
               nsl_id: str = None,
               profile_name: str = None,
               auto_paginate: bool = False,
               only_accessible: bool = False) -> Iterator[stac_pb2.StacItem]:
        """
        search for stac items by using StacRequest. return a stream of StacItems
        :param timeout: timeout for request
        :param stac_request: StacRequest of query parameters to filter by
        :param nsl_id: ADVANCED ONLY. Only necessary if more than one nsl_id and nsl_secret have been defined with
        set_credentials method.  Specify nsl_id to use. if NSL_ID and NSL_SECRET environment variables not set must use
        NSLClient object's set_credentials to set credentials
        :param profile_name: if a ~/.nsl/credentials file exists, you can override the [default] credential usage, by
        using a different profile name
        :param auto_paginate:
            - if specified, this will automatically paginate and yield all received StacItems.
            - If `stac_request.limit` is specified, only the that amount of StacItems will be yielded.
            - If `stac_request.offset` is specified, pagination will begin at that `offset`.
            - If set to `False` (the default), `stac_request.limit` and `stac_request.offset` can be used to manually
                page through StacItems.
        :param only_accessible: limits results to only StacItems downloadable by your level of sample/paid access
        :return: stream of StacItems
        """
        for item in self._search_all(stac_request,
                                     timeout,
                                     nsl_id=nsl_id,
                                     profile_name=profile_name,
                                     auto_paginate=auto_paginate):
            if not only_accessible or \
                    bearer_auth.is_valid_for(item_region(item), nsl_id=nsl_id, profile_name=profile_name):
                yield item

    def search_collections(self,
                           collection_request: stac_pb2.CollectionRequest,
                           timeout=15,
                           nsl_id: str = None,
                           profile_name: str = None) -> Iterator[stac_pb2.Collection]:
        metadata = (('authorization', bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)),)
        for item in self._stac_service.stub.SearchCollections(collection_request, timeout=timeout, metadata=metadata):
            yield item

    def subscribe(self,
                  stac_request: stac_pb2.StacRequest,
                  destination: BaseDestination,
                  nsl_id: str = None,
                  profile_name: str = None,
                  is_active=True) -> str:
        """
        Creates a subscription to a `StacRequest`, to deliver matching `StacItem`s to a `BaseDestination`.
        """
        assert stac_request.updated == TimestampFilter(), \
            "cannot subscribe to StacRequests with a set `updated` timestamp filter"
        assert not (isinstance(destination, MemoryDestination) or destination.__class__ == BaseDestination), \
            "cannot create subscriptions that deliver to `BaseDestination`s or `MemoryDestination`s"

        if self._nsl_only:
            stac_request.mission_enum = stac_pb2.SWIFT
        res = requests.post(f'{AUTH0_TENANT}/subscription',
                            headers=NSLClient._json_headers(nsl_id, profile_name),
                            json=dict(stac_request=utils.stac_request_to_b64(stac_request),
                                      destination=destination.to_json_str(),
                                      is_active=is_active))

        NSLClient._handle_json_response(res, 201)
        sub_id = res.json()['sub_id']
        print(f'created subscription with id: {sub_id}')
        return sub_id

    def resubscribe(self, sub_id: str, nsl_id: str = None, profile_name: str = None):
        """Reactivates a subscription with the given `sub_id`."""
        res = requests.put(f'{AUTH0_TENANT}/subscription/{sub_id}',
                           headers=NSLClient._json_headers(nsl_id, profile_name))

        NSLClient._handle_json_response(res, 200)
        print(f'reactivated subscription with id: {sub_id}')
        return

    def unsubscribe(self, sub_id: str, nsl_id: str = None, profile_name: str = None):
        """Deactivates a subscription with the given `sub_id`."""
        res = requests.delete(f'{AUTH0_TENANT}/subscription/{sub_id}',
                              headers=NSLClient._json_headers(nsl_id, profile_name))

        NSLClient._handle_json_response(res, 202)
        print(f'deactivated subscription with id: {sub_id}')
        return

    def subscriptions(self, nsl_id: str = None, profile_name: str = None) -> List[Subscription]:
        """Fetches all subscriptions."""
        res = requests.get(f'{AUTH0_TENANT}/subscription',
                           headers=NSLClient._json_headers(nsl_id, profile_name))

        NSLClient._handle_json_response(res, 200)
        return list(Subscription(response_dict) for response_dict in res.json()['results'])

    def _search_all(self,
                    stac_request: stac_pb2.StacRequest,
                    timeout=15,
                    nsl_id: str = None,
                    profile_name: str = None,
                    auto_paginate: bool = False) -> Iterator[stac_pb2.StacItem]:
        # limit to only search Near Space Labs SWIFT data
        if self._nsl_only:
            stac_request.mission_enum = stac_pb2.SWIFT

        if not auto_paginate:
            metadata = (('authorization', bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)),)
            for item in self._stac_service.stub.SearchItems(stac_request, timeout=timeout, metadata=metadata):
                if not item.id:
                    warn("STAC item missing STAC id; ending search")
                    return
                else:
                    yield item
        else:
            limit = stac_request.limit if stac_request.limit > 0 else None
            offset = stac_request.offset
            page_size = 500
            count = 0

            stac_request.limit = page_size
            items = list(self.search(stac_request, timeout=timeout, nsl_id=nsl_id, profile_name=profile_name))
            while len(items) > 0:
                for item in items:
                    if limit is None or (limit is not None and count < limit):
                        yield item
                        count += 1
                    if limit is not None and count >= limit:
                        break

                if limit is not None and count >= limit:
                    break

                stac_request.offset += page_size
                items = list(self.search(stac_request, timeout=timeout, nsl_id=nsl_id, profile_name=profile_name))

            stac_request.offset = offset
            stac_request.limit = limit if limit is not None else 0

    @staticmethod
    def _json_headers(nsl_id: str = None, profile_name: str = None) -> dict:
        return {'content-type': 'application/json',
                'Authorization': bearer_auth.auth_header(nsl_id=nsl_id, profile_name=profile_name)}

    @staticmethod
    def _handle_json_response(res, status_code: int):
        if res.status_code != status_code:
            raise requests.exceptions.RequestException(f'non-nominal status code: {res.status_code}')
        elif len(res.content) == 0:
            # then if response is empty, HTTPResponse method for read returns b"" which will be zero in length
            raise requests.exceptions.RequestException("empty authentication return. notify nsl of error")
