import sys
import pickle
import traceback
from functools import wraps

import transaction
from pyramid.paster import get_appsettings
from uwsgidecorators import cron
import uwsgi

from planevent.redisdb import redis_db
from planevent import (
    createSQLConnection,
    settings,
    redisdb,
    logger,
)


spooler_functions = {}


def _bytes(obj):
    return bytes(str(obj), 'utf8')


def spool_function_wrapper(fun, *args, **kwargs):
    try:
        redisdb.createConnections()
        createSQLConnection(get_appsettings(settings.INI_FILE))
        with transaction.manager:
            fun(*args, **kwargs)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logger.error(
            '{} task failed. Reason: {}\nStack:\n{}'
            .format(fun.__name__, str(e), ''.join(trace))
        )
    finally:
        # return uwsgi.SPOOL_RETRY
        return uwsgi.SPOOL_OK


def manage_spool_request(vars):
    spool_function = spooler_functions[vars[b'spool_function']]
    kwargs = pickle.loads(vars.pop(b'kwargs'))
    args = pickle.loads(vars.pop(b'args'))
    return spool_function_wrapper(spool_function, *args, **kwargs)


uwsgi.spooler = manage_spool_request


class async(object):

    def __call__(self, *args, **kwargs):
        arguments = self.base_dict
        spooler_args = {}
        for key in ('message_dict', 'spooler', 'priority', 'at', 'body'):
            if key in kwargs:
                spooler_args.update({key: kwargs.pop(key)})
        arguments.update(spooler_args)
        arguments[b'args'] = pickle.dumps(args)
        arguments[b'kwargs'] = pickle.dumps(kwargs)
        return uwsgi.spool(arguments)

    def __init__(self, f):
        if not 'spooler' in uwsgi.opt:
            raise Exception(
                "you have to enable the uWSGI spooler to use @async decorator"
            )
        self.f = f
        fun_name = _bytes(self.f.__name__)
        spooler_functions[fun_name] = f
        self.base_dict = {
            _bytes('spool_function'): fun_name
        }


def progress_counter(mth):
    @wraps(mth)
    def wrap(*args, **kwargs):
        counter = None
        for param in list(args) + list(kwargs.values()):
            if isinstance(param, TaskProgressCounter):
                counter = param
                break

        try:
            counter.start()
            result = mth(*args, **kwargs)
            if counter:
                counter.finish()
            return result
        except Exception as e:
            if counter:
                message = '{} {}'.format(e.__class__.__name__, str(e))
                logger.info(
                    'Marking task {} progress as failed. Reason: {}'
                    .format(counter.id, message)
                )
                counter.mark_as_failed(message)
            raise e
    return wrap


class TaskProgressCounter(object):

    COUNTER_KEY = 'tasks:progresscounter:sequence'
    PROGRESS_KEY = 'tasks:progresscounter:{}:progress'

    PENDING = 'PENDING'
    WORKING = 'WORKING'
    FINISHED = 'FINISHED'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'

    @classmethod
    def create(cls):
        counter = TaskProgressCounter()
        counter.id = redis_db.incr(cls.COUNTER_KEY)
        counter._max = 1
        counter._progress = 0
        counter.status = cls.PENDING
        counter._message = ''

        counter._save_progress()

        return counter

    @classmethod
    def get(cls, id_):
        data = redis_db.get(cls.PROGRESS_KEY.format(id_))
        if data is None:
            raise ValueError('No task with id {}'.format(id_))
        else:
            progress, max_, status, message = data.split(';')

            counter = TaskProgressCounter()

            counter.id = id_
            counter._max = max_
            counter._progress = progress
            counter.status = status
            counter._message = message

            return counter

    @classmethod
    def cancel(cls, id_):
        progress = cls.get(id_)
        progress.status = cls.CANCELED
        progress._save_progress()

    def is_canceled(self):
        self.status = TaskProgressCounter.get(self.id).status
        return self.status == self.CANCELED

    def mark_as_failed(self, message):
        self.status = self.FAILED
        self._message = message
        self._save_progress()

    def _save_progress(self):
        key = self.PROGRESS_KEY.format(self.id)

        redis_db.set(
            key,
            '{};{};{};{}'
            .format(self._progress, self._max, self.status, self._message))

        redis_db.expire(key, 7200)

    def start(self):
        self.status = self.WORKING
        self._save_progress()

    def finish(self):
        if self.status == self.WORKING:
            self.status = self.FINISHED
            self._progress = self._max
            self._save_progress()

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
        if self._progress >= self._max:
            self.status = self.FINISHED
        self._save_progress()

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self._save_progress()
