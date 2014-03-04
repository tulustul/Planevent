import planevent
from planevent import (
    models,
    services,
    settings,
    sql,
)
from planevent.async import (
    async,
    cron,
    progress_counter,
)
from planevent.scripts.initializedb import (
    create_test_vendor,
    create_test_categories,
    create_test_tags,
    TestInstances,
)


@async
def send_welcome_email(account):
    services.send_mail(
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
        services.send_mail(
            template='recomendations',
            to=account.email,
            subject='Planevent - dzisiejsze rekomendacje',
            account=account,
        )


@async
@progress_counter
def generate_random_tasks(quantity, progress_counter):
    progress_counter.message = 'Flushing database'
    progress_counter.max = quantity

    sql.Base.metadata.drop_all(planevent.sql_engine)
    sql.Base.metadata.create_all(planevent.sql_engine)
    categories, subcategories = create_test_categories()
    tags = create_test_tags()

    progress_counter.message = 'Generating entities'
    for i in range(quantity):
        create_test_vendor(TestInstances(tags, categories, subcategories))

        if i % 10 == 0:
            if progress_counter.is_canceled():
                return
            else:
                progress_counter.progress += 10

    progress_counter.message = '{} entities generated'.format(quantity)
