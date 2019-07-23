import sys
import os

from setuptools import setup, find_packages

src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
old_path = os.getcwd()
os.chdir(src_path)
sys.path.insert(0, src_path)

kwargs = {
    'name': 'st.stac',
    'description': 'gRPC Spatio Temporal Asset Catalog library',
    'url': 'https://github.com/Swiftera/stac-client-python',
    'long_description': "gRPC Spatio Temporal Asset Catalog library",
    'author': 'David Raleigh',
    'author_email': 'david@swiftera.co',
    'license': 'Apache 2.0',
    'version': '0.0.7',
    'namespace_package': ['st'],
    'python_requires': '>3.5.2',
    'packages': ['st.stac'],
    'install_requires': [
        'grpcio-tools',
        'protobuf',
        'shapely',
        'epl.protobuf'
    ],
    'zip_safe': False
}

clssfrs = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
kwargs['classifiers'] = clssfrs

setup(**kwargs)
