import planevent
from planevent import (
    models,
    mailing,
    settings,
    logger,
    sql,
)
from planevent.async import (
    async,
    cron,
)
from planevent.scripts.initializedb import (
    create_test_vendor,
    create_test_categories,
    create_test_tags,
    TestInstances,
)
from planevent.redisdb import redis_db


class TaskProgressCounter(object):

    COUNTER_KEY = 'tasks:progresscounter:sequence'
    PROGRESS_KEY = 'tasks:progresscounter:{}:progress'

    def __init__(self):
        self.id = redis_db.incr(self.COUNTER_KEY)
        self._max = 1
        self._progress = 0

        self._save_progress()

    @classmethod
    def get_progress(cls, id_):
        progress = redis_db.get(cls.PROGRESS_KEY.format(id_))
        if progress is None:
            raise ValueError('No task with id {}'.format(id_))
        else:
            return [int(val) for val in progress.split('/')]

    def _save_progress(self):
        key = self.PROGRESS_KEY.format(self.id)
        redis_db.set(key, '{}/{}'.format(self._progress, self._max))
        redis_db.expire(key, 7200)

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        self._max = value
        self._save_progress()

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self._save_progress()


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
def generate_random_tasks(quantity, progress_counter):
    progress_counter.max = quantity

    sql.Base.metadata.drop_all(planevent.sql_engine)
    sql.Base.metadata.create_all(planevent.sql_engine)
    categories, subcategories = create_test_categories()
    tags = create_test_tags()

    for i in range(quantity):
        create_test_vendor(TestInstances(tags, categories, subcategories))

        progress_counter.progress += 1
