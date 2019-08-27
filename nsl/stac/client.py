import os

from typing import Iterator

from epl.protobuf import stac_pb2

from nsl.stac import stac_service


def insert_one(stac_item: stac_pb2.StacItem) -> stac_pb2.StacDbResponse:
    """
    Insert on item into the service
    :param stac_item: item to insert
    :return: StacDbResponse, the response of the success of the insert
    """
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    return stac_service.stub.InsertOne(stac_item, metadata=(
        ('authorization', auth),
        ('bearer', bearer),
    ))


def search_one(stac_request: stac_pb2.StacRequest) -> stac_pb2.StacItem:
    """
    search for one item from the db that matches the stac request
    :param stac_request: StacRequest of query parameters to filter by
    :return: StacItem
    """
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    return stac_service.stub.SearchOne(stac_request, metadata=(
        ('authorization', auth),
        ('bearer', bearer),
    ))


def count(stac_request: stac_pb2.StacRequest) -> int:
    """
    count all the items in the database that match the stac request
    :param stac_request: StacRequest query parameters to apply to count method (limit ignored)
    :return: int
    """
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    db_result = stac_service.stub.Count(stac_request, metadata=(
        ('authorization', auth),
        ('bearer', bearer),
    ))
    return db_result.count


def search(stac_request: stac_pb2.StacRequest) -> Iterator[stac_pb2.StacItem]:
    """
    search for stac items by using StacRequest. return a stream of StacItems
    :param stac_request: StacRequest of query parameters to filter by
    :return: stream of StacItems
    """
    auth = os.getenv('AUTH')
    bearer = os.getenv('BEARER')
    results_generator = stac_service.stub.Search(stac_request, metadata=(
        ('authorization', auth),
        ('bearer', bearer),
    ))
    return results_generator
