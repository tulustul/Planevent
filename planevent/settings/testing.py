from celery.schedules import crontab

CELERY_TIMEZONE = 'Europe/Warsaw'

CELERYBEAT_SCHEDULE = {
    'send_recomendations_emails': {
        'task': 'planevent.tasks.send_recomendations_emails',
        'schedule': crontab(minute=0, hour=2),
    },
}

INI_FILE = 'testing.ini'

APP_URL = 'http://localhost:8080'

TEST_INSTANCES = 0

REDIS = {
    'URL': 'localhost',
    'PORT': 6379,
    'CACHE_DB': 15,
    'DB': 14,
    'CELERY_DB': 13,
    'PASSWORD': '',
}
