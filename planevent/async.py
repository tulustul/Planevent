import pickle
import transaction

from pyramid.paster import get_appsettings
from uwsgidecorators import cron
import uwsgi

from planevent import (
    createSQLConnection,
    settings,
    redisdb,
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
        return uwsgi.SPOOL_OK
    except:
        return uwsgi.SPOOL_RETRY


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
