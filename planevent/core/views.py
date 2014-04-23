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
from planevent.core.decorators import (
    permission,
    route,
    Template,
)


class View(object):

    def __init__(self, request):
        self.request = request

    def response(self, code=200, message=None, **kwargs):
        self.request.response.status = code
        if message:
            kwargs['message'] = message
        return kwargs

    def get_user_dict(self):
        return self.request.session.get('user')

    def _get_user_field(self, field, default_value=None):
        user = self.get_user_dict()
        return user[field] if user else default_value

    def get_user_id(self):
        return self._get_user_field('id')

    def get_user_role(self):
        return self._get_user_field('role', Account.Role.ANONYMOUS)

    def get_user_email(self):
        return self._get_user_field('email')


@route('home')
class HomeView(View):
    def get(self) -> Template('index'):
        return {'PIWIK_URL': settings.PIWIK_URL}


@route('admin')
class AdminView(View):
    @permission(Account.Role.ADMIN)
    def get(self) -> Template('admin'):
        return {}


@notfound_view_config()
def notfound(request):
    return Response('Not found, dude!', status='404 Not Found')


@forbidden_view_config()
def forbidden(request):
    return Response('You are not allowed', status='401 Unauthorized')
