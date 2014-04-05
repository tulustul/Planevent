from planevent import (
    services,
    settings,
)
from planevent.async import async


@async
def send_welcome_email(account):
    services.send_mail(
        template='welcome',
        to=account.email,
        subject='Sie ma',
        account=account,
        app_url=settings.APP_URL,
    )


@async
def send_password_recall_email(account):
    services.send_mail(
        template='password_recall',
        to=account.email,
        subject='Planevent - przypomnienie hasła',
        account=account,
        app_url=settings.APP_URL,
    )
