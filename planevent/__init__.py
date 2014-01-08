import datetime

from pyramid.config import Configurator
from pyramid.renderers import JSON
from sqlalchemy import engine_from_config

from planevent.models import (
    DBSession,
    Base,
)
from planevent.urls import urls


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    json_renderer = JSON()
    def datetime_adapter(obj, request):
        return obj.isoformat()
    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    config.add_renderer('json', json_renderer)

    config.include('pyramid_chameleon')
    config.add_static_view('static', '../static', cache_max_age=3600)
    for url_config in urls:
        config.add_route(*url_config)
    config.scan()
    return config.make_wsgi_app()
