from planevent import (
    models,
    mailing,
    settings,
)
from planevent.async import (
    async,
    cron,
)
from planevent.scripts.initializedb import create_test_instances


@async
def send_welcome_email(account):
    mailing.send(
        template='welcome',
        to=account.email,
        subject='Sie ma',
        account=account,
        app_url=settings.APP_URL,
    )


@cron(1, 1, -1, -1, -1)
def send_recomendations_emails(num):
    accounts = models.Account().all()

    for account in accounts:
        mailing.send(
            template='recomendations',
            to=account.email,
            subject='Planevent - dzisiejsze rekomendacje',
            account=account,
        )


@async
def generate_random_tasks(quantity):
    create_test_instances(quantity)
