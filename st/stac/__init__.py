import os
import re

import grpc

from epl.protobuf import stac_service_pb2_grpc

STAC_METADATA_SERVICE = "{0}:{1}".format(os.getenv('STAC_SERVICE_HOST', 'localhost'),
                                         os.getenv('STAC_SERVICE_PORT', 10000))

BYTES_IN_MB = 1024 * 1024
# at this point only allowing 4 MB or smaller messages
MESSAGE_SIZE_MB = 4
GRPC_CHANNEL_OPTIONS = [('grpc.max_message_length', MESSAGE_SIZE_MB * BYTES_IN_MB),
                        ('grpc.max_receive_message_length', MESSAGE_SIZE_MB * BYTES_IN_MB)]

# TODO prep for ip v6
IP_REGEX = re.compile(r"[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}")


class __StacServiceStub(object):
    def __init__(self):
        print("connecting to stac service at: {}\n".format(STAC_METADATA_SERVICE))
        # TODO host env should include http:// so we can just see if it's https or http
        if STAC_METADATA_SERVICE.startswith("localhost") or \
                IP_REGEX.match(STAC_METADATA_SERVICE) or \
                "." not in STAC_METADATA_SERVICE:
            channel = grpc.insecure_channel(STAC_METADATA_SERVICE, options=GRPC_CHANNEL_OPTIONS)
        else:
            channel_credentials = grpc.ssl_channel_credentials()
            channel = grpc.secure_channel(STAC_METADATA_SERVICE,
                                          credentials=channel_credentials,
                                          options=GRPC_CHANNEL_OPTIONS)

        self._channel = channel
        self._stub = stac_service_pb2_grpc.StacServiceStub(channel)

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


stac_service = __StacServiceStub()
