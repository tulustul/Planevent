from planevent import services
from planevent.async import cron
from planevent.accounts.models import Account


@cron(1, 1, -1, -1, -1)
def send_recomendations_emails(num):
    accounts = Account().filter(
        Account.use_recommendations==True,
    ).all()

    for account in accounts:
        services.send_mail(
            template='recomendations',
            recipients=account.email,
            subject='Planevent - dzisiejsze rekomendacje',
            account=account,
        )
