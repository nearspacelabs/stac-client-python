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

import abc
import os
import re
import http.client
import json
import math
import sched
import time
import warnings
import logging

import grpc

from pathlib import Path
from random import randint
from typing import Optional, Tuple, Dict

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage as gcp_storage
from google.oauth2 import service_account

from epl.protobuf.v1 import stac_service_pb2_grpc
from epl.protobuf.v1.geometry_pb2 import GeometryData, ProjectionData, EnvelopeData
from epl.protobuf.v1.query_pb2 import TimestampFilter, FloatFilter, StringFilter, UInt32Filter
from epl.protobuf.v1.stac_pb2 import StacRequest, StacItem, Asset, LandsatRequest, Eo, EoRequest, Mosaic, \
    MosaicRequest, DatetimeRange, View, ViewRequest

__all__ = [
    'stac_service', 'url_to_channel', 'STAC_SERVICE',
    'EoRequest', 'StacRequest', 'LandsatRequest', 'MosaicRequest', 'ViewRequest',
    'GeometryData', 'ProjectionData', 'EnvelopeData',
    'FloatFilter', 'TimestampFilter', 'StringFilter', 'UInt32Filter',
    'StacItem', 'Asset', 'Eo', 'View', 'Mosaic', 'DatetimeRange',
    'gcs_storage_client',
    'AUTH0_TENANT', 'API_AUDIENCE', 'ISSUER', 'bearer_auth'
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

# URL of the OAuth service
AUTH0_TENANT = os.getenv('AUTH0_TENANT', 'api.nearspacelabs.net')
# Name of the API for which we issue tokens
API_AUDIENCE = os.getenv('API_AUDIENCE', 'https://api.nearspacelabs.com')
# Name of the service responsible for issuing NSL tokens
ISSUER = 'https://api.nearspacelabs.net/'

TOKEN_REFRESH_THRESHOLD = 60  # seconds
TOKEN_REFRESH_SCHEDULER = sched.scheduler(time.time, time.sleep)
MAX_TOKEN_REFRESH_BACKOFF = 60
MAX_TOKEN_ATTEMPTS = 20

MAX_GRPC_ATTEMPTS = int(os.getenv('MAX_ATTEMPTS', 4))
INIT_BACKOFF_MS = int(os.getenv('INIT_BACKOFF_MS', 4))
MAX_BACKOFF_MS = int(os.getenv('MAX_BACKOFF_MS', 4))
MULTIPLIER = int(os.getenv('MULTIPLIER', 4))

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
NSL_CREDENTIALS = Path(Path.home(), '.nsl', 'credentials')

logger = logging.getLogger()


class SleepingPolicy(abc.ABC):
    @abc.abstractmethod
    def sleep(self, try_i: int):
        """
        How long to sleep in milliseconds.
        :param try_i: the number of retry (starting from zero)
        """
        assert try_i >= 0


# Retry mechanism
# https://github.com/grpc/grpc/issues/19514#issuecomment-531700657
class ExponentialBackoff(SleepingPolicy):
    def __init__(self, *, init_backoff_ms: int, max_backoff_ms: int, multiplier: int):
        self.init_backoff = randint(0, init_backoff_ms)
        self.max_backoff = max_backoff_ms
        self.multiplier = multiplier

    def sleep(self, try_i: int):
        sleep_range = min(self.init_backoff * self.multiplier ** try_i, self.max_backoff)
        sleep_ms = randint(0, sleep_range)
        logger.debug(f"Sleeping for {sleep_ms}")
        time.sleep(sleep_ms / 1000)


class RetryOnRpcErrorClientInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.StreamUnaryClientInterceptor):
    def __init__(self,
                 *,
                 max_attempts: int,
                 sleeping_policy: SleepingPolicy,
                 status_for_retry: Optional[Tuple[grpc.StatusCode]] = None):
        self.max_attempts = max_attempts
        self.sleeping_policy = sleeping_policy
        self.status_for_retry = status_for_retry

    def _intercept_call(self, continuation, client_call_details, request_or_iterator):
        for try_i in range(self.max_attempts):
            response = continuation(client_call_details, request_or_iterator)

            if isinstance(response, grpc.RpcError):

                # Return if it was last attempt
                if try_i == (self.max_attempts - 1):
                    return response

                # If status code is not in retryable status codes
                if self.status_for_retry and response.code() not in self.status_for_retry:
                    return response

                self.sleeping_policy.sleep(try_i)
            else:
                return response

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return self._intercept_call(continuation, client_call_details, request_iterator)


interceptors = (
    RetryOnRpcErrorClientInterceptor(
        max_attempts=MAX_GRPC_ATTEMPTS,
        sleeping_policy=ExponentialBackoff(init_backoff_ms=INIT_BACKOFF_MS,
                                           max_backoff_ms=MAX_BACKOFF_MS,
                                           multiplier=MULTIPLIER),
        status_for_retry=(grpc.StatusCode.UNAVAILABLE,),
    ),
)


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

    return grpc.intercept_channel(channel, *interceptors)


class __GCSStorageClient:
    _client = None

    @property
    def client(self):
        if self._client is not None:
            return self._client

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
        self._client = client
        return self._client


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


class AuthInfo:
    nsl_id: str = None
    nsl_secret: str = None
    token: Dict = None
    retries: int = 0
    expiry: float = 0

    def __init__(self, nsl_id, nsl_secret):
        if not nsl_id or not nsl_secret:
            raise ValueError("nsl_id and nsl_secret must be non-zero length strings")
        self.nsl_id = nsl_id
        self.nsl_secret = nsl_secret

    def authorize(self, backoff: int = 0):
        if self.retries >= MAX_TOKEN_ATTEMPTS:
            raise Exception("NSL authentication failed over 20 times")

        print("attempting NSL authentication against {}".format(AUTH0_TENANT))
        now = time.time()
        try:
            conn = http.client.HTTPSConnection(AUTH0_TENANT)
            headers = {'content-type': 'application/json'}
            post_body = {
                'client_id': self.nsl_id,
                'client_secret': self.nsl_secret,
                'audience': API_AUDIENCE,
                'grant_type': 'client_credentials'
            }

            conn.request("POST", "/oauth/token", json.dumps(post_body), headers)
            res = conn.getresponse()

            # evaluate codes first.
            # then if response is empty, HTTPResponse method for read returns b"" which will be zero in length
            res_body = res.read()
            if (res.getcode() != 200 and res.getcode() != 201) or len(res_body) == 0:
                warnings.warn("authentication failed with code {0}".format(res.getcode()))

                # TODO make this non-recursive
                self.retry(backoff)
                return

            res_json = json.loads(res_body.decode("utf-8"))

            self.retries = 0
            self.expiry = now + int(res_json["expires_in"])
            self.token = res_json["access_token"]
        except json.JSONDecodeError as je:
            warnings.warn("failed to decode authentication json token with error: {}".format(je))
            self.retry(backoff)
            return
        except BaseException as be:
            warnings.warn("failed to connect to authorization service with error: {0}".format(be))
            self.retry(backoff)
            return

    def retry(self, timeout: int = 0):
        """Retry authorization request, with exponential backoff"""
        self.retries += 1
        backoff = min(2 if timeout == 0 else timeout * 2, MAX_TOKEN_REFRESH_BACKOFF)
        TOKEN_REFRESH_SCHEDULER.enter(backoff, 1, self.authorize, argument=[backoff])
        TOKEN_REFRESH_SCHEDULER.run()


class __BearerAuth:
    _auth_info_map: Dict[str, AuthInfo] = {}
    _profile_map: Dict[str, str] = {}
    _default_nsl_id = None

    def __init__(self, init=False):
        if (not NSL_ID or not NSL_SECRET) and not NSL_CREDENTIALS.exists():
            warnings.warn("NSL_ID and NSL_SECRET environment variables not set")
            return
        if NSL_ID and NSL_SECRET:
            self._auth_info_map[NSL_ID] = AuthInfo(nsl_id=NSL_ID, nsl_secret=NSL_SECRET)
            self._default_nsl_id = NSL_ID
        elif NSL_CREDENTIALS:
            with NSL_CREDENTIALS.open('r') as file_obj:
                lines = file_obj.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('['):
                        if not lines[i + 1].startswith('NSL_ID') or not lines[i + 2].startswith('NSL_SECRET'):
                            raise ValueError("credentials should be of the format:\n[named profile]\nNSL_ID={your "
                                             "nsl id}\nNSL_SECRET={your nsl secret}")
                        # for id like 'NSL_ID = all_the_id_text\n', first strip remove front whitespace and newline
                        # .strip(), now we now [6:] starts after 'NSL_ID' .strip()[6:], strip potential whitespace
                        # between NSL_ID and '=' with .strip()[6:].strip(), start one after equal
                        # .strip()[6:].strip()[1:], strip potential whitespace
                        # after equal .strip()[6:].strip()[1:].strip()
                        nsl_id = lines[i + 1].strip()[6:].strip()[1:].strip()
                        nsl_secret = lines[i + 2].strip()[10:].strip()[1:].strip()
                        self._auth_info_map[nsl_id] = AuthInfo(nsl_id=nsl_id, nsl_secret=nsl_secret)
                        if 'default' in line:
                            self._default_nsl_id = nsl_id
                        self._profile_map[line.strip().lstrip('[').rstrip(']')] = nsl_id

        if init:
            self._auth_info_map[self._default_nsl_id].authorize()

    @property
    def default_nsl_id(self):
        return self._default_nsl_id

    def set_credentials(self, nsl_id: str, nsl_secret: str):
        if len(self._auth_info_map) == 0:
            self._default_nsl_id = nsl_id

        self._auth_info_map[nsl_id] = AuthInfo(nsl_id=nsl_id, nsl_secret=nsl_secret)
        self._auth_info_map[nsl_id].authorize()

    def auth_header(self, nsl_id: str = None, profile_name: str = None):
        if nsl_id is None and profile_name is None:
            nsl_id = self._default_nsl_id

        if nsl_id not in self._auth_info_map and profile_name not in self._profile_map:
            raise ValueError("credentials must be set by environment variables NSL_ID & NSL_SECRET or by using the "
                             "set_credentials method, or by setting a credentials file at ~/.nsl/credentials")

        if profile_name is not None:
            print('using profile name: {}'.format(profile_name))
            nsl_id = self._profile_map[profile_name]

        if (self._auth_info_map[nsl_id].expiry - time.time()) < TOKEN_REFRESH_THRESHOLD:
            self._auth_info_map[nsl_id].authorize()
            diff_seconds = self._auth_info_map[nsl_id].expiry - time.time()
            print("fetching new authorization in {0} minutes".format(
                round(int(math.ceil(float(diff_seconds / 60) / 10) * 10))))
        return "Bearer {token}".format(token=self._auth_info_map[nsl_id].token)


time.sleep(NSL_NETWORK_DELAY)
bearer_auth = __BearerAuth()
stac_service = __StacServiceStub()
gcs_storage_client = __GCSStorageClient()
