import sys
import os

from setuptools import setup

src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
old_path = os.getcwd()
os.chdir(src_path)
sys.path.insert(0, src_path)

kwargs = {
    'name': 'nsl.stac',
    'description': 'gRPC Spatio Temporal Asset Catalog library',
    'url': 'https://github.com/nearspacelabs/stac-client-python',
    'long_description': "gRPC Spatio Temporal Asset Catalog library provided by Near Space Labs",
    'author': 'David Raleigh',
    'author_email': 'david@swiftera.co',
    'license': 'Apache 2.0',
    'version': '0.2.15',
    'python_requires': '>3.6.0',
    'packages': ['nsl.stac'],
    'install_requires': [
        'grpcio-tools',
        'protobuf',
        'shapely',
        'epl.protobuf',
        'boto3',
        'google-cloud-storage'
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
