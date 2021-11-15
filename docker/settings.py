from .base_settings import *
from google.oauth2 import service_account
import os

INSTALLED_APPS += [
    'sis_provisioner.apps.BridgeProvisionerConfig',
]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_SSL_CERTFILE = os.getenv('CERT_PATH', '')
EMAIL_SSL_KEYFILE = os.getenv('KEY_PATH', '')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_TIMEOUT = 60

RESTCLIENTS_DEFAULT_CONNECT_TIMEOUT = 300
if os.getenv('BRIDGE_ENV') in RESTCLIENTS_DEFAULT_ENVS:
    RESTCLIENTS_BRIDGE_DAO_CLASS = 'Live'
    RESTCLIENTS_BRIDGE_TIMEOUT = os.getenv(
        'BRIDGE_TIMEOUT', RESTCLIENTS_DEFAULT_TIMEOUT)
    RESTCLIENTS_BRIDGE_POOL_SIZE = os.getenv(
        'BRIDGE_POOL_SIZE', RESTCLIENTS_DEFAULT_POOL_SIZE)
    RESTCLIENTS_BRIDGE_BASIC_AUTH_KEY = os.getenv('BRIDGE_BASIC_AUTH_KEY', '')
    RESTCLIENTS_BRIDGE_BASIC_AUTH_SECRET = os.getenv('BRIDGE_BASIC_AUTH_SECRET', '')
    if os.getenv('BRIDGE_ENV') == 'PROD':
        RESTCLIENTS_BRIDGE_HOST = 'https://uw.bridgeapp.com:443'
    else:
        RESTCLIENTS_BRIDGE_HOST = 'https://uwtest.bridgeapp.com:443'

if os.getenv('ENV', 'localdev') == 'localdev':
    DEBUG = True
    BRIDGE_AUTHOR_GROUP_NAME = 'u_bridgeap_authors'
    BRIDGE_IMPORT_USER_FILE_SIZE = 3
    BRIDGE_LOGIN_WINDOW = 0
    ERRORS_TO_ABORT_LOADER = []
    RESTCLIENTS_DAO_CACHE_CLASS = None
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = os.getenv('IMPORT_CSV_ROOT', '/data')
else:
    RESTCLIENTS_DAO_CACHE_CLASS = 'sis_provisioner.cache.BridgeAccountCache'
    BRIDGE_USER_WORK_POSITIONS = 2
    BRIDGE_AUTHOR_GROUP_NAME = os.getenv('AUTHOR_GROUP')
    BRIDGE_CHECK_ALL_ACCOUNTS = os.getenv('CHECK_ALL_ACCOUNTS')
    BRIDGE_LOGIN_WINDOW = os.getenv('LOGIN_WINDOW', 1)
    BRIDGE_GMEMBER_ADD_WINDOW = os.getenv('GMEMBER_ADD_WINDOW')
    BRIDGE_GMEMBER_DEL_WINDOW = os.getenv('GMEMBER_DEL_WINDOW')
    BRIDGE_PERSON_CHANGE_WINDOW = os.getenv('PERSON_CHANGE_WINDOW')
    BRIDGE_WORKER_CHANGE_WINDOW = os.getenv('WORKER_CHANGE_WINDOW')
    BRIDGE_CRON_SENDER = os.getenv('BRIDGE_CRON_SENDER', '')
    RESTCLIENTS_DISABLE_THREADING = True
    ERRORS_TO_ABORT_LOADER = [401, 403, 500, 502, 503]

    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_PROJECT_ID = os.getenv('STORAGE_PROJECT_ID', '')
    GS_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME', '')
    GS_LOCATION = os.path.join(os.getenv('IMPORT_CSV_ROOT', ''))
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        '/gcs/credentials.json')

LOGGING['formatters'] = {
    'std': {
        'format': '%(name)s %(levelname)-4s %(asctime)s %(message)s',
    },
}
LOGGING['handlers']['stdout']['formatter'] = 'std'
LOGGING['handlers']['stderr']['formatter'] = 'std'
