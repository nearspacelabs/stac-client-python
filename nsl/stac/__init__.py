import os
import re

import grpc

from epl.protobuf import stac_service_pb2_grpc

STAC_SERVICE = os.getenv('STAC_SERVICE', 'localhost:10000')
BYTES_IN_MB = 1024 * 1024
# at this point only allowing 4 MB or smaller messages
MESSAGE_SIZE_MB = int(os.getenv('MESSAGE_SIZE_MB', 4))
GRPC_CHANNEL_OPTIONS = [('grpc.max_message_length', MESSAGE_SIZE_MB * BYTES_IN_MB),
                        ('grpc.max_receive_message_length', MESSAGE_SIZE_MB * BYTES_IN_MB)]

# TODO prep for ip v6
IP_REGEX = re.compile(r"[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}")
# DEFAULT Insecure until we have a https service
INSECURE = True


def url_to_channel(stac_service_url):
    if stac_service_url.startswith("localhost") or IP_REGEX.match(stac_service_url) or \
            "." not in stac_service_url or stac_service_url.startswith("http://") or INSECURE:
        stac_service_url = stac_service_url.strip("http://")
        channel = grpc.insecure_channel(stac_service_url, options=GRPC_CHANNEL_OPTIONS)
    else:
        stac_service_url = stac_service_url.strip("https://")
        channel_credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(stac_service_url,
                                      credentials=channel_credentials,
                                      options=GRPC_CHANNEL_OPTIONS)

    return channel


def _generate_grpc_channel(stac_service_url=None):
    # TODO host env should include http:// so we can just see if it's https or http

    if stac_service_url is None:
        stac_service_url = STAC_SERVICE

    channel = url_to_channel(stac_service_url)

    print("nsl client connecting to stac service at: {}\n".format(stac_service_url))

    return channel, stac_service_pb2_grpc.StacServiceStub(channel)


class __StacServiceStub(object):
    def __init__(self):
        channel, stub = _generate_grpc_channel()
        self._channel = channel
        self._stub = stub

    @property
    def channel(self):
        return self._channel

    @property
    def stub(self):
        return self._stub

    def set_channel(self, channel):
        """
        This allows you to override the channel created on init, with another channel. This might be needed if multiple
        libraries are using the same channel, or if multi-threading.
        :param channel:
        :return:
        """
        self._stub = stac_service_pb2_grpc.StacServiceStub(channel)
        self._channel = channel

    def update_service_url(self, stac_service_url):
        """allows you to update your stac service address"""
        self._channel, self._stub = _generate_grpc_channel(stac_service_url=stac_service_url)


stac_service = __StacServiceStub()
