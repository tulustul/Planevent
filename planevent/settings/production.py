from celery.schedules import crontab

CELERY_TIMEZONE = 'Europe/Warsaw'

CELERYBEAT_SCHEDULE = {
    'send_recomendations_emails': {
        'task': 'planevent.tasks.send_recomendations_emails',
        'schedule': crontab(minute=0, hour=2),
    },
}

INI_FILE = 'production.ini'

APP_URL = 'http://planevent-tul.rhcloud.com'

TEST_INSTANCES = 3000

REDIS = {
    'URL': '127.10.51.3',
    'PORT': 16379,
    'CACHE_DB': 0,
    'CELERY_DB': 1,
    'DB': 0,
    'PASSWORD': 'ZTNiMGM0NDI5OGZjMWMxNDlhZmJmNGM4OTk2ZmI5',
}
