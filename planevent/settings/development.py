from celery.schedules import crontab

CELERY_TIMEZONE = 'Europe/Warsaw'

CELERYBEAT_SCHEDULE = {
    'send_recomendations_emails': {
        'task': 'planevent.tasks.send_recomendations_emails',
        'schedule': crontab(minute=0, hour=2),
    },
}

INI_FILE = 'development.ini'

APP_URL = 'http://localhost:8080'

TEST_INSTANCES = 300

REDIS = {
    'URL': 'localhost',
    'PORT': 6379,
    'CACHE_DB': 0,
    'CELERY_DB': 1,
    'DB': 0,
    'PASSWORD': '',
}
