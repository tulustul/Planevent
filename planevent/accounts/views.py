from pyramid.httpexceptions import HTTPFound

from planevent.accounts import (
    models,
    auth,
    oauth,
)
from planevent.core.decorators import (
    permission,
    route,
    Rest,
    Body,
)
from planevent.core.views import View
from planevent.services.mailing import InvalidEmail
from planevent import settings


@route('register')
class RegisterView(View):

    def post(self, credentials: Body(str)):
        try:
            email, password = credentials.split(':', 1)
        except:
            return self.response(400, 'invalid_body')

        try:
            return auth.register(self.request, email, password)
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


@route('login')
class LoginView(View):

    def post(self, credentials: Body(str)):
        try:
            email, password = credentials.split(':', 1)
        except:
            return self.response(400, 'invalid_body')
        try:
            auth.try_login(self.request, email, password)
        except (InvalidEmail, auth.InvalidCredentials):
            return self.response(400, 'invalid_credentials')
        else:
            return models.Account.get_by_email(email)


@route('login_oauth2')
class LoginOAuthView(View):

    def get(self, provider: Rest(str)):
        return HTTPFound(
            location=oauth.login_oauth(self.request, provider)
        )


@route('oauth2_callback')
class OAuth2CallbackView(View):

    def get(self, provider: Rest(str)):
        return HTTPFound(
            location=oauth.process_oauth_callback(self.request, provider)
        )


@route('logout')
class LogoutView(View):

    @permission(models.Account.Role.NORMAL)
    def post(self):
        auth.logout(self.request)
        return self.response(200, 'logged_out')


@route('change_password')
class ChangePasswordView(View):

    def post(self, credentials: Body(str)):
        email = self.get_user_email()
        if not email:
            return self.response(403, 'not_logged_in')

        try:
            old_password, new_password = credentials.split(':', 1)
        except ValueError:
            return self.response(400, 'invalid_body')

        try:
            auth.change_password(email, old_password, new_password)
        except (InvalidEmail, auth.InvalidCredentials):
            return self.response(400, 'invalid_credentials')

        return self.response(200, 'password_changed')


@route('password_recall')
class PasswordRecallView(View):

    def post(self, email: Body(str)):
        try:
            auth.recall_password(email)
        except InvalidEmail:
            return self.response(400, 'invalid_email')
        return self.response(200, 'mail_sent')


@route('password_recall_callback')
class PasswordRecallCallbackView(View):

    def post(self, credentials: Body(str)):
        try:
            token, new_password = credentials.split(':', 1)
        except ValueError:
            return self.response(400, 'invalid_body')

        try:
            auth.recall_password_callback(token, new_password)
        except auth.InvalidToken:
            return self.response(400, 'invalid_token')
        except auth.TokenExpired:
            return self.response(400, 'token_expired')
        except models.Account.PasswordToShort:
            return self.response(
                400,
                'password_to_short',
                mimimum_length=settings.MINIMUM_PASSWORD_LENGTH,
            )
        return self.response(200, 'password_set')


@route('logged_user')
class LoggedUserView(View):

    @permission(models.Account.Role.NORMAL)
    def get(self):
        user_id = self.get_user_id()
        if user_id:
            return models.Account.get(
                user_id,
                'settings',
                'settings.address',
                'likings',
                'likings.subcategory',
            )
        return

    def post(self, account: Body(models.Account)):
        user_id = self.get_user_id()
        if account.id != user_id:
            return self.response(401, 'Can edit only owned account')

        account.save()
        return account
