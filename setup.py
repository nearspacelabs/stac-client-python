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

import sys
import os

from setuptools import setup

src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
old_path = os.getcwd()
os.chdir(src_path)
sys.path.insert(0, src_path)

package_name = 'nsl.stac'
kwargs = {
    'name': package_name,
    'description': 'gRPC Spatio Temporal Asset Catalog library',
    'url': 'https://github.com/nearspacelabs/stac-client-python',
    'long_description': "gRPC Spatio Temporal Asset Catalog library provided by Near Space Labs",
    'author': 'David Raleigh',
    'author_email': 'david@nearspacelabs.com',
    'license': 'Apache 2.0',
    'version': '1.2.1',
    'python_requires': '>3.6.0',
    'packages': ['nsl.stac', 'nsl.stac.destinations'],
    'install_requires': [
        'boto3',
        'epl.protobuf.v1',
        'google-cloud-storage',
        'grpcio-tools',
        'protobuf',
        'requests',
        'retry',
    ],
    'zip_safe': False
}

clssfrs = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]
kwargs['classifiers'] = clssfrs

setup(**kwargs)
