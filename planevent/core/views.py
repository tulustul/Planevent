from pyramid.view import (
    view_config,
    forbidden_view_config,
    notfound_view_config,
)
from pyramid.response import Response

from planevent import (
    settings,
)
from planevent.accounts.models import Account
from planevent.core.decorators import permission


class View(object):

    def __init__(self, request):
        self.request = request

    def response(self, code=200, message=None, **kwargs):
        self.request.response.status = code
        if message:
            kwargs['message'] = message
        return kwargs

    def get_user(self):
        return Account.get(self.request.session.get('user_id'))

    def get_user_role(self):
        user_role = self.request.session.get('user_role')
        if user_role:
            return user_role
        else:
            return Account.Role.ANONYMOUS


@view_config(route_name='home', renderer='../templates/index.jinja2')
def home_view(self):
    return {'PIWIK_URL': settings.PIWIK_URL}


class AdminView(View):
    @view_config(route_name='admin', renderer='../templates/admin.jinja2')
    @permission(Account.Role.ADMIN)
    def get(self):
        return {}


@notfound_view_config()
def notfound(request):
    return Response('Not found, dude!', status='404 Not Found')


@forbidden_view_config()
def forbidden(request):
    return Response('You are not allowed', status='401 Unauthorized')
