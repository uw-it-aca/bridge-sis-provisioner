import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

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
        'Django>=2.0.13,<2.1',
        'python-dateutil',
        'UW-RestClients-Core>=1.2.1,<2.0',
        'UW-RestClients-PWS>=2.1,<3.0',
        'UW-RestClients-GWS>=2.2.4,<3.0',
        'uw-restclients-hrp>=1.2.1,<2.0',
        'uw-restclients-bridge>=1.5.2,<2.0',
        'UW-RestClients-Django-Utils<3.0',
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
        'Programming Language :: Python :: 3.6',
    ],
)
