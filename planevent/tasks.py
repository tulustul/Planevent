from celery import Celery

from pyramid.paster import get_appsettings

from planevent import (
    models,
    mailing,
    settings,
    createSQLConnection,
)

broker_url = 'redis://:{0}@{1}:{2}/{3}'.format(
    settings.REDIS['PASSWORD'],
    settings.REDIS['URL'],
    settings.REDIS['PORT'],
    settings.REDIS['CELERY_DB'],
)

celery = Celery('tasks', broker=broker_url)

# TODO celery beat opens unnecessary connection here
createSQLConnection(get_appsettings(settings.INI_FILE))


@celery.task
def send_welcome_email(account):
    mailing.send(
        template='welcome',
        to=account.email,
        subject='Sie ma',
        account=account,
        app_url=settings.APP_URL,
    )


@celery.task
def send_recomendations_emails():
    accounts = models.Account().all()

    for account in accounts:
        mailing.send(
            template='recomendations',
            to=account.email,
            subject='Planevent - dzisiejsze rekomendacje',
            account=account,
        )
