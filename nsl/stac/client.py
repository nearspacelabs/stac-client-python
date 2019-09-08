import os

from typing import Iterator

from epl.protobuf import stac_pb2

from nsl.stac import stac_service as stac_singleton


class NSLClient:
    def __init__(self):
        self._stac_service = stac_singleton
        self._auth = os.getenv('AUTH')
        self._bearer = os.getenv('BEARER')

    def update_service_url(self, stac_service_url):
        """
        update the stac service address
        :param stac_service_url: localhost:8080, 34.34.34.34:9000, http://demo.nearspacelabs.com, etc
        :return:
        """
        self._stac_service.update_service_url(stac_service_url=stac_service_url)

    def insert_one(self, stac_item: stac_pb2.StacItem) -> stac_pb2.StacDbResponse:
        """
        Insert on item into the stac service
        :param stac_item: item to insert
        :return: StacDbResponse, the response of the success of the insert
        """
        return self._stac_service.stub.InsertOne(stac_item, metadata=(
            ('authorization', self._auth),
            ('bearer', self._bearer),
        ))

    def search_one(self, stac_request: stac_pb2.StacRequest) -> stac_pb2.StacItem:
        """
        search for one item from the db that matches the stac request
        :param stac_request: StacRequest of query parameters to filter by
        :return: StacItem
        """
        return self._stac_service.stub.SearchOne(stac_request, metadata=(
            ('authorization', self._auth),
            ('bearer', self._bearer),
        ))

    def count(self, stac_request: stac_pb2.StacRequest) -> int:
        """
        count all the items in the database that match the stac request
        :param stac_request: StacRequest query parameters to apply to count method (limit ignored)
        :return: int
        """
        db_result = self._stac_service.stub.Count(stac_request, metadata=(
            ('authorization', self._auth),
            ('bearer', self._bearer),
        ))
        return db_result.count

    def search(self, stac_request: stac_pb2.StacRequest) -> Iterator[stac_pb2.StacItem]:
        """
        search for stac items by using StacRequest. return a stream of StacItems
        :param stac_request: StacRequest of query parameters to filter by
        :return: stream of StacItems
        """
        results_generator = self._stac_service.stub.Search(stac_request, metadata=(
            ('authorization', self._auth),
            ('bearer', self._bearer),
        ))
        return results_generator
