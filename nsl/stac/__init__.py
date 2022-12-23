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
import base64
import os
import re
import json
import math
import time
import warnings
import logging

import grpc
import requests

from dataclasses import dataclass
from pathlib import Path
from random import randint
from typing import Dict, Optional, Set, Tuple

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage as gcp_storage
from google.oauth2 import service_account
from retry import retry

from epl.protobuf.v1 import stac_service_pb2_grpc
from epl.protobuf.v1.geometry_pb2 import GeometryData, ProjectionData, EnvelopeData
from epl.protobuf.v1.query_pb2 import TimestampFilter, FloatFilter, StringFilter, UInt32Filter
from epl.protobuf.v1.stac_pb2 import StacRequest, StacItem, Asset, Collection, CollectionRequest, Eo, EoRequest, \
    LandsatRequest, Mosaic, MosaicRequest, DatetimeRange, View, ViewRequest, Extent, Interval, Provider

__all__ = [
    'stac_service', 'url_to_channel', 'STAC_SERVICE',
    'Collection', 'CollectionRequest', 'EoRequest', 'StacRequest', 'LandsatRequest', 'MosaicRequest', 'ViewRequest',
    'GeometryData', 'ProjectionData', 'EnvelopeData',
    'FloatFilter', 'TimestampFilter', 'StringFilter', 'UInt32Filter',
    'StacItem', 'Asset', 'Eo', 'View', 'Mosaic', 'DatetimeRange', 'Extent', 'Interval', 'Provider',
    'gcs_storage_client',
    'AUTH0_TENANT', 'API_AUDIENCE', 'ISSUER', 'AuthInfo', 'bearer_auth'
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
AUTH0_TENANT = os.getenv('AUTH0_TENANT', 'https://api.nearspacelabs.net')
# Name of the API for which we issue tokens
API_AUDIENCE = os.getenv('API_AUDIENCE', 'https://api.nearspacelabs.com')
# Name of the service responsible for issuing NSL tokens
ISSUER = 'https://api.nearspacelabs.net/'

TOKEN_REFRESH_THRESHOLD = 60  # seconds

MAX_GRPC_ATTEMPTS = int(os.getenv('MAX_ATTEMPTS', 4))
INIT_BACKOFF_MS = int(os.getenv('INIT_BACKOFF_MS', 4))
MAX_BACKOFF_MS = int(os.getenv('MAX_BACKOFF_MS', 4))
MULTIPLIER = int(os.getenv('MULTIPLIER', 4))

STAC_SERVICE = os.getenv('STAC_SERVICE', 'api.nearspacelabs.net:9090')
BYTES_IN_MB = 1024 * 1024
# at this point only allowing 4 MB or smaller messages
MESSAGE_SIZE_MB = int(os.getenv('MESSAGE_SIZE_MB', 20))
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


@dataclass
class Contract:
    balance: int
    region: int
    type: str

    @staticmethod
    def from_jwt(token: str):
        payload = json.loads(base64.b64decode(token.split('.')[1] + '=='))
        contract = payload[f'{API_AUDIENCE}/contract']
        return Contract(balance=contract['balance'], region=contract['region'], type=contract['type'])

    def is_valid_for(self, region: str) -> bool:
        if self.region == 1 or region == 'REGION_0' or region == 'SAMPLES':
            return True

        if region == "REGION_1":
            masked = self.region & 2
        elif region == "REGION_2":
            masked = self.region & 4
        elif region == "REGION_3":
            masked = self.region & 8
        elif region == "REGION_4":
            masked = self.region & 16
        elif region == "REGION_5":
            masked = self.region & 32
        elif region == "REGION_6":
            masked = self.region & 64
        elif region == "REGION_7":
            masked = self.region & 128
        else:
            return False
        return masked != 0 and masked <= self.region


class AuthInfo:
    nsl_id: str = None
    nsl_secret: str = None
    token: str = None
    expiry: float = 0
    skip_authorization: bool = False
    contract: Contract

    def __init__(self, nsl_id: str, nsl_secret: str):
        if not nsl_id or not nsl_secret:
            raise ValueError("nsl_id and nsl_secret must be non-zero length strings")
        self.nsl_id = nsl_id
        self.nsl_secret = nsl_secret

    # this only retries if there's a timeout error
    @retry(exceptions=requests.Timeout, delay=1, backoff=2, tries=4)
    def authorize(self):
        if self.skip_authorization:
            return

        expiry, token = AuthInfo.get_token_client_credentials(self.nsl_id, self.nsl_secret)
        self.expiry = expiry
        self.token = token
        self.contract = Contract.from_jwt(token)

    @property
    def permissions(self) -> Set[str]:
        _, payload, _ = self.token.split('.')
        payload = json.loads(base64.b64decode(payload + '==='))
        return {permission for permission in payload.get('permissions', set())}

    @staticmethod
    def get_token_client_credentials(nsl_id: str, nsl_secret: str,
                                     auth_url=f"{AUTH0_TENANT}/oauth/token",
                                     grant_type: str = 'client_credentials',
                                     additional_headers: dict = None):
        print(f"attempting NSL authentication against {auth_url}...")
        now = time.time()

        if additional_headers is None:
            additional_headers = dict()

        headers = {'content-type': 'application/json', **additional_headers}
        post_body = {
            'client_id': nsl_id,
            'client_secret': nsl_secret,
            'audience': API_AUDIENCE,
            'grant_type': grant_type,
        }

        res = requests.post(auth_url, json=post_body, headers=headers)

        if res.status_code != 200 and res.status_code != 201:
            # evaluate codes first.
            message = f"authentication failed with code '{res.status_code}' and reason '{res.reason}'"
            raise requests.exceptions.RequestException(message)
        elif len(res.content) == 0:
            # then if response is empty, HTTPResponse method for read returns b"" which will be zero in length
            raise requests.exceptions.RequestException("empty authentication return. notify nsl of error")

        print(f"successfully authenticated with NSL_ID: `{nsl_id}`")
        res_json = res.json()
        expiry = now + int(res_json['expires_in'])
        token = res_json['access_token']
        return expiry, token


class __BearerAuth:
    _auth_info_map: Dict[str, AuthInfo] = {}
    _profile_map: Dict[str, str] = {}
    _default_nsl_id = None

    def __init__(self, init=False):
        if (not NSL_ID or not NSL_SECRET) and not NSL_CREDENTIALS.exists():
            warnings.warn(f"NSL_ID and NSL_SECRET environment variables not set, and {NSL_CREDENTIALS} does not exist")
            return

        # if credentials exist, add them to our auth store
        if NSL_CREDENTIALS and NSL_CREDENTIALS.exists():
            for profile_name, auth_info in self.loads().items():
                self._auth_info_map[auth_info.nsl_id] = auth_info
                if profile_name == 'default':
                    self._default_nsl_id = auth_info.nsl_id
                self._profile_map[profile_name] = auth_info.nsl_id
                print(f"found NSL_ID {auth_info.nsl_id} under profile name `{profile_name}`")

        # if env vars were specified, add them as well and set them to the default
        if NSL_ID and NSL_SECRET:
            print(f"using NSL_ID {NSL_ID} specified in env var")
            self._auth_info_map[NSL_ID] = AuthInfo(nsl_id=NSL_ID, nsl_secret=NSL_SECRET)
            self._default_nsl_id = NSL_ID

        # if env vars are unset and no NSL_ID was tagged as default, use the first one available
        if self.default_nsl_id is None:
            self._default_nsl_id = list(key for key in self._auth_info_map.keys())[0]
            print(f"using NSL_ID {self.default_nsl_id}")

        if init:
            self._auth_info_map[self._default_nsl_id].authorize()

    @property
    def default_nsl_id(self):
        return self._default_nsl_id

    def auth_header(self, nsl_id: str = None, profile_name: str = None):
        auth_info = self._get_auth_info(nsl_id, profile_name)
        if not auth_info.skip_authorization and (auth_info.expiry - time.time()) < TOKEN_REFRESH_THRESHOLD:
            print(f'authorizing NSL_ID: `{auth_info.nsl_id}`')
            auth_info.authorize()
            diff_seconds = auth_info.expiry - time.time()
            ttl = round(int(math.ceil(float(diff_seconds / 60) / 10) * 10))
            print(f"will attempt re-authorization in {ttl} minutes")
        return f"Bearer {auth_info.token}"

    def get_credentials(self, nsl_id: str = None) -> Optional[AuthInfo]:
        return self._auth_info_map.get(nsl_id if nsl_id is not None else self.default_nsl_id, None)

    def set_credentials(self, nsl_id: str, nsl_secret: str):
        if len(self._auth_info_map) == 0:
            self._default_nsl_id = nsl_id

        self._auth_info_map[nsl_id] = AuthInfo(nsl_id=nsl_id, nsl_secret=nsl_secret)
        self._auth_info_map[nsl_id].authorize()

    def unset_credentials(self, profile_name: str):
        nsl_id = self._profile_map.pop(profile_name)
        delattr(self._auth_info_map, nsl_id)
        if self._default_nsl_id == nsl_id:
            if len(self._auth_info_map) == 0:
                self._default_nsl_id = None
            else:
                self._default_nsl_id = list(key for key in self._auth_info_map.keys())[0]
                print(f"using NSL_ID {self.default_nsl_id}")

    def is_valid_for(self, region: str, nsl_id: str = None, profile_name: str = None) -> bool:
        auth_info = self._get_auth_info(nsl_id=nsl_id, profile_name=profile_name)
        return auth_info.contract.is_valid_for(region)

    def loads(self) -> Dict[str, AuthInfo]:
        output = dict()
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
                    profile_name = line.strip().lstrip('[').rstrip(']')
                    nsl_id = lines[i + 1].strip()[6:].strip()[1:].strip()
                    nsl_secret = lines[i + 2].strip()[10:].strip()[1:].strip()

                    output[profile_name] = AuthInfo(nsl_id=nsl_id, nsl_secret=nsl_secret)
        return output

    def dumps(self):
        with NSL_CREDENTIALS.open('w') as file_obj:
            for profile_name, nsl_id in self._profile_map.items():
                creds = self.get_credentials(nsl_id)
                file_obj.write(f'[{profile_name}]\n')
                file_obj.write(f'NSL_ID={creds.nsl_id}\n')
                file_obj.write(f'NSL_SECRET={creds.nsl_secret}\n')
                file_obj.write('\n')
            file_obj.close()

    def _get_auth_info(self, nsl_id: str = None, profile_name: str = None) -> AuthInfo:
        if nsl_id is None and profile_name is None:
            nsl_id = self._default_nsl_id

        if nsl_id not in self._auth_info_map and profile_name not in self._profile_map:
            raise ValueError("credentials must be set by environment variables NSL_ID & NSL_SECRET, by setting a "
                             "credentials file at ~/.nsl/credentials, or by using the set_credentials method")

        if profile_name is not None:
            nsl_id = self._profile_map[profile_name]
        return self._auth_info_map[nsl_id]


time.sleep(NSL_NETWORK_DELAY)
bearer_auth = __BearerAuth()
stac_service = __StacServiceStub()
gcs_storage_client = __GCSStorageClient()
