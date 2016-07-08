from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^support', include('userservice.urls')),
    url(r'^support/', include('userservice.urls')),
    url(r'^restclients', include('restclients.urls')),
    url(r'^', include('sis_provisioner.urls')),
]
