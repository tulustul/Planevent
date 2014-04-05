from pyramid.view import (
    view_config,
)

from planevent import (
    settings,
)


class View(object):

    def __init__(self, request):
        self.request = request

    def response(self, code=200, message=None, **kwargs):
        self.request.response.status = code
        kwargs['message'] = message
        return kwargs


@view_config(route_name='home', renderer='../templates/index.jinja2')
def home_view(request):
    return {'PIWIK_URL': settings.PIWIK_URL}


@view_config(route_name='admin', renderer='../templates/admin.jinja2')
def admin_view(request):
    return {}
