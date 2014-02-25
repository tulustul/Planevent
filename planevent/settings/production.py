from celery.schedules import crontab

CELERY_TIMEZONE = 'Europe/Warsaw'

CELERYBEAT_SCHEDULE = {
    'send_recomendations_emails': {
        'task': 'planevent.tasks.send_recomendations_emails',
        'schedule': crontab(minute='*'),
    },
}

INI_FILE = 'production.ini'

APP_URL = 'http://planevent-tul.rhcloud.com'

TEST_INSTANCES = 1000

REDIS = {
    'URL': '127.10.51.3',
    'PORT': 16379,
    'CACHE_DB': 0,
    'DB': 1,
    'CELERY_DB': 2,
    'PASSWORD': 'ZTNiMGM0NDI5OGZjMWMxNDlhZmJmNGM4OTk2ZmI5',
}
