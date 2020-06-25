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

import os
import re
import http.client
import json
import sched
import time
import warnings

import grpc

from epl.protobuf import stac_service_pb2_grpc
from epl.protobuf.geometry_pb2 import GeometryData, SpatialReferenceData, EnvelopeData
from epl.protobuf.query_pb2 import TimestampField, FloatField, StringField, UInt32Field
from epl.protobuf.stac_pb2 import StacRequest, StacItem, Asset, LandsatRequest, Eo, EoRequest, Mosaic, MosaicRequest, \
    DatetimeRange

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage as gcp_storage
from google.oauth2 import service_account

__all__ = [
    'stac_service', 'url_to_channel', 'STAC_SERVICE',
    'EoRequest', 'StacRequest', 'LandsatRequest', 'MosaicRequest',
    'GeometryData', 'SpatialReferenceData', 'EnvelopeData',
    'FloatField', 'TimestampField', 'StringField', 'UInt32Field',
    'StacItem', 'Asset', 'Eo', 'Mosaic', 'DatetimeRange',
    'gcs_storage_client', 'bearer_auth'
]

CLOUD_PROJECT = os.getenv("CLOUD_PROJECT")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SERVICE_ACCOUNT_DETAILS = os.getenv("SERVICE_ACCOUNT_DETAILS")

NSL_ID = os.getenv("NSL_ID")
NSL_SECRET = os.getenv("NSL_SECRET")
# if an application uses this package, this singleton pattern of using an __init__.py file means that the package
# and all the network calls will be made immediately upon application start. In some cases a virtual machine might
# be able to start an application before it has network access.
NSL_NETWORK_DELAY = int(os.getenv("NSL_NETWORK_DELAY", 0))

AUTH0_TENANT = os.getenv('AUTH0_TENANT', 'nearspacelabs.auth0.com')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'https://api.nearspacelabs.com')
TOKEN_REFRESH_THRESHOLD = 60  # seconds
TOKEN_REFRESH_SCHEDULER = sched.scheduler(time.time, time.sleep)
MAX_TOKEN_REFRESH_BACKOFF = 60


STAC_SERVICE = os.getenv('STAC_SERVICE', 'api.nearspacelabs.net:9090')
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


def _get_storage_client():
    # TODO remove SERVICE_ACCOUNT_DETAILS
    if SERVICE_ACCOUNT_DETAILS:
        details = json.loads(SERVICE_ACCOUNT_DETAILS)
        creds = service_account.Credentials.from_service_account_info(details)
        client = gcp_storage.Client(project=CLOUD_PROJECT, credentials=creds)
    elif GOOGLE_APPLICATION_CREDENTIALS:
        creds = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
        client = gcp_storage.Client(project=CLOUD_PROJECT, credentials=creds)
    else:
        try:
            # https://github.com/googleapis/google-auth-library-python/issues/271#issuecomment-400186626
            warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")
            client = gcp_storage.Client(project="")
        except DefaultCredentialsError:
            client = None

    return client


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
        self._channel, self._stub = _generate_grpc_channel(stac_service_url)


class __BearerAuth:
    _expiry = 0
    _token = {}

    def __init__(self):
        if not NSL_ID or not NSL_SECRET:
            warnings.warn("NSL_ID and NSL_SECRET should both be set")
        else:
            self.authorize()

    def auth_header(self):
        if (bearer_auth.expiry - time.time()) < TOKEN_REFRESH_THRESHOLD:
            print("re-authorize bearer expiration {0}, threshold (in seconds) {1}"
                  .format(bearer_auth.expiry, time.time(), TOKEN_REFRESH_THRESHOLD))
            self.authorize()
        return "Bearer {token}".format(token=self._token)

    def authorize(self):
        print("attempting NSL authentication against {}".format(AUTH0_TENANT))
        try:
            conn = http.client.HTTPSConnection(AUTH0_TENANT)
            headers = {'content-type': 'application/json'}
            post_body = {
                'client_id': NSL_ID,
                'client_secret': NSL_SECRET,
                'audience': API_AUDIENCE,
                'grant_type': 'client_credentials'
            }

            conn.request("POST", "/oauth/token", json.dumps(post_body), headers)
            res = conn.getresponse()

            if res.code != 200:
                warnings.warn("authentication error code {0}".format(res.code))

            res_body = json.loads(res.read().decode("utf-8"))
            if "error" in res_body:
                warnings.warn("authentication failed with error '{0}' and message '{1}'"
                              .format(res_body["error"], res_body["error_description"]))
                self.retry()
                return

            self._expiry = res_body["expires_in"] + time.time()
            self._token = res_body["access_token"]
        except json.JSONDecodeError:
            warnings.warn("failed to decode authentication json token")
            self._expiry = 0
            self._token = {}
        except BaseException as be:
            warnings.warn("failed to connect to authorization service with error: {0}".format(be))
            self._expiry = 0
            self._token = {}

    @property
    def expiry(self):
        return self._expiry

    def retry(self, timeout: int = 0):
        """Retry authorization request, with exponential backoff"""
        backoff = min(2 if timeout == 0 else timeout * 2, MAX_TOKEN_REFRESH_BACKOFF)
        TOKEN_REFRESH_SCHEDULER.enter(backoff, 1, self.authorize)
        TOKEN_REFRESH_SCHEDULER.run()


time.sleep(NSL_NETWORK_DELAY)
bearer_auth = __BearerAuth()
stac_service = __StacServiceStub()
gcs_storage_client = _get_storage_client()
