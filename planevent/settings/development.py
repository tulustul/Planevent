from planevent.settings.shared import *

INI_FILE = 'development.ini'

APP_URL = 'http://localhost:8080'

REDIS = {
    'URL': 'localhost',
    'PORT': 6379,
    'CACHE_DB': 0,
    'DB': 1,
    'PASSWORD': '',
}

ADMINS = ADMINS + [User(
    name='test account',
    email='test.account@example.com',
    password='asdasd',
)]

USE_PERMISSIONS = False
