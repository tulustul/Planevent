import pyramid

from planevent import (
    models,
    tasks,
)
from planevent.services import mailing


class AuthException(Exception):
    pass


class InvalidCredentials(AuthException):
    pass


class EmailAlreadyTaken(AuthException):
    pass


def register(request, email, password):
    mailing.validate_email(email)

    account = models.Account.get_by_email(email)

    if account:
        raise EmailAlreadyTaken()

    account = models.Account.create(
        email=email,
    )

    account.name = email.split('@')[0]
    account.first_name = account.name

    account.set_password(password)
    account.save()

    request.session['user_id'] = account.id

    tasks.send_welcome_email(account)


def change_password(email, old_password, new_password):
    account = models.Account.get_by_email(email, 'credentials')
    authenticate_account(account, old_password)

    account.set_password(new_password)
    account.save()


def racall_password(email):
    account = models.Account.get_by_email(email, 'credentials')
    account.forget_password()
    account.save()
    tasks.send_password_recall_email(account)


def racall_password_callback(email):
    pass


def authenticate_account(account, password):
    if not account:
        raise InvalidCredentials()

    if not account.check_password(password):
        raise InvalidCredentials()


def login(request, email, password):
    account = models.Account.get_by_email(email, 'credentials')
    authenticate_account(account, password)
    request.session['user_id'] = account.id


def logout(request):
    request.session['user_id'] = None
    pyramid.security.forget()
    return request.route_url('home')
