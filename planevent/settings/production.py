from planevent.settings.shared import *

INI_FILE = 'production.ini'

APP_URL = 'http://planevent-tul.rhcloud.com'

REDIS = {
    'URL': '127.10.51.3',
    'PORT': 16379,
    'CACHE_DB': 0,
    'DB': 1,
    'PASSWORD': 'ZTNiMGM0NDI5OGZjMWMxNDlhZmJmNGM4OTk2ZmI5',
}

PIWIK_URL = 'piwik-tul.rhcloud.com/'

ADMINS = ADMINS + [User(
    name='Van Black',
    email='slawomir.jablonski@gmail.com',
    password='admin',
    avatar=None,
)]
