from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

from planevent.accounts import (
    models,
    auth,
)
from planevent.core.decorators import param
from planevent.core.views import View
from planevent.services.mailing import InvalidEmail
from planevent import settings


@view_defaults(route_name='register', renderer='json')
class RegisterView(View):

    @view_config(request_method='POST')
    @param('credentials', str, required=True, body=True)
    def post(self, credentials):
        email, password = credentials.split(':', 1)
        try:
            auth.register(self.request, email, password)
        except auth.EmailAlreadyTaken:
            return self.response(409, 'email_already_taken')
        except InvalidEmail:
            return self.response(400, 'invalid_email')
        except models.Account.PasswordToShort:
            return self.response(
                400,
                'password_to_short',
                mimimum_length=settings.MINIMUM_PASSWORD_LENGTH,
            )
        else:
            return self.response(201, 'account_created')


@view_defaults(route_name='login', renderer='json')
class LoginView(View):

    @view_config(request_method='POST')
    @param('credentials', str, required=True, body=True)
    def post(self, credentials):
        email, password = credentials.split(':', 1)
        try:
            auth.try_login(self.request, email, password)
        except (InvalidEmail, auth.InvalidCredentials):
            return self.response(400, 'invalid_credentials')
        else:
            return self.response(200, 'logged_in')


@view_defaults(route_name='login_oauth2')
class LoginOAuthView(View):

    @view_config(request_method='GET')
    @param('provider', str, required=True, rest=True)
    def get(self, provider):
        return HTTPFound(
            location=auth.login_oauth(self.request, provider)
        )


@view_defaults(route_name='oauth2_callback', renderer='json')
class OAuth2CallbackView(View):

    @view_config(request_method='GET')
    @param('provider', str, required=True, rest=True)
    def get(self, provider):
        return HTTPFound(
            location=auth.process_oauth_callback(self.request, provider)
        )


@view_defaults(route_name='logout', renderer='json')
class LogoutView(View):

    @view_config(request_method='POST')
    def post(self):
        auth.logout(self.request)
        return self.response(200, 'logged_out')


@view_defaults(route_name='password_recall', renderer='json')
class PasswordRecallView(View):

    @view_config(request_method='POST')
    @param('email', str, required=True, body=True)
    def post(self, email):
        try:
            auth.recall_password_callback(email)
        except InvalidEmail:
            return self.response(400, 'invalid_email')
        return self.response(200, 'mail_sent')


@view_defaults(route_name='logged_user', renderer='json')
class LoggedUserView(View):

    @view_config(request_method='GET')
    def get(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            return models.Account.get(
                user_id,
                'settings',
                'settings.address',
                'likings',
                'likings.subcategory',
            )
        return

    @view_config(request_method='POST')
    @param('account', models.Account, body=True, required=True)
    def post(self, account):
        user_id = self.request.session.get('user_id')
        if account.id != user_id:
            self.request.response.status = 401
            return {
                'error': 'Can edit only owned account'
            }

        account.save()
        return account
