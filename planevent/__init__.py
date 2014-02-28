import datetime
import os
import logging

from pyramid_beaker import session_factory_from_settings
from pyramid.config import Configurator
from pyramid.renderers import JSON
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings


from planevent.core import sql
from planevent.urls import urls
from planevent import redisdb
from planevent import settings as app_settings

os.environ['DEBUG'] = '1'

logger = logging.getLogger('planevent')

sql_engine = None


def createSQLConnection(settings):
    global sql_engine
    if not sql_engine:
        sql_engine = engine_from_config(settings, 'sqlalchemy.')
        sql.DBSession.configure(bind=sql_engine)
        sql.Base.metadata.bind = sql_engine


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    createSQLConnection(get_appsettings(app_settings.INI_FILE))
    redisdb.createConnections()

    config = Configurator(settings=settings)

    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    json_renderer = JSON()

    def datetime_adapter(obj, request):
        return obj.isoformat()
    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    config.add_renderer('json', json_renderer)

    config.add_static_view('static', '../static', cache_max_age=3600)

    for url_config in urls:
        config.add_route(*url_config)

    config.scan()

    return config.make_wsgi_app()
