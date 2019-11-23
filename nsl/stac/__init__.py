import os
import re
import http.client
import json
import time
import warnings

import grpc

from epl.protobuf import stac_service_pb2_grpc
from google.cloud import storage as gcp_storage
from google.oauth2 import service_account

CLOUD_PROJECT = os.getenv("CLOUD_PROJECT")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SERVICE_ACCOUNT_DETAILS = os.getenv("SERVICE_ACCOUNT_DETAILS")

NSL_ID = os.getenv("NSL_ID")
NSL_SECRET = os.getenv("NSL_SECRET")

# TODO:
API_AUDIENCE = "http://localhost:8000"
AUTH0_DOMAIN = "swiftera-dev.auth0.com"
TOKEN_REFRESH_THRESHOLD = 300  # 5 minutes

STAC_SERVICE = os.getenv('STAC_SERVICE', 'eap.nearspacelabs.net:9090')
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
        self.authorize()

    def auth_header(self):
        return "Bearer {token}".format(token=self._token)

    def authorize(self):
        conn = http.client.HTTPSConnection(AUTH0_DOMAIN)
        headers = {'content-type': 'application/json'}
        post_body = {
            'client_id': NSL_ID,
            'client_secret': NSL_SECRET,
            'audience': API_AUDIENCE,
            'grant_type': 'client_credentials'
        }

        conn.request("POST", "/oauth/token", json.dumps(post_body), headers)
        res = conn.getresponse()

        # TODO: handle failure and retries
        res_body = json.loads(res.read().decode("utf-8"))
        self._expiry = res_body["expires_in"] + time.time()
        self._token = res_body["access_token"]

    @property
    def expiry(self):
        return self._expiry


class AuthGuard:
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        if (bearer_auth.expiry - time.time()) < TOKEN_REFRESH_THRESHOLD:
            bearer_auth.authorize()

        return self.f(*args, **kwargs)


bearer_auth = __BearerAuth()
stac_service = __StacServiceStub()
gcs_storage_client = _get_storage_client()
