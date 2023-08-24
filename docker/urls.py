# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from .base_urls import *
from django.urls import re_path
from django.conf.urls import include

urlpatterns += [
    re_path(r'^', include('sis_provisioner.urls')),
]
