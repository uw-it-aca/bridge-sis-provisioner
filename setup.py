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
    name='bridge-sis-provisioner',
    version=VERSION,
    packages=['sis_provisioner'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires = [
        'Django',
        'ordereddict',
        'urllib3==1.10.2',
        'unittest2',
        'django-compressor',
        'django-templatetag-handlebars',
        'nameparser>=0.2.8'
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
        'Programming Language :: Python :: 2.7',
    ],
)
