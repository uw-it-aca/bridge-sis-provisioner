# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/bridge-sis-provisioner>`_.
"""

version_path = 'sis_provisioner/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url='https://github.com/uw-it-aca/bridge-sis-provisioner'

setup(
    name='Bridge-Acount-Provisioner',
    version=VERSION,
    packages=['sis_provisioner'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires = [
        'Django~=3.2',
        'python-dateutil',
        'pytz',
        'django-storages[google]>=1.10',
        'uw-memcached-clients~=1.0',
        'UW-RestClients-Core~=1.3',
        'UW-RestClients-PWS~=2.1',
        'UW-RestClients-GWS~=2.3',
        'uw-restclients-hrp~=1.3',
        'uw-restclients-bridge~=1.6',
        'freezegun',
    ],
    license='Apache License, Version 2.0',
    description='An Django application that provisions UW users to Bridge',
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
)
