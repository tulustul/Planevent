from datetime import datetime

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


def _authenticate_account(account, password):
    if not account:
        raise InvalidCredentials()

    if not account.check_password(password):
        raise InvalidCredentials()


def _login(request, account):
    account.last_login = datetime.now()
    account.login_count += 1
    account.save()
    request.session['user_id'] = account.id


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
    account.last_login = datetime.now()

    account.set_password(password)

    _login(request, account)

    tasks.send_welcome_email(account)


def change_password(email, old_password, new_password):
    account = models.Account.get_by_email(email, 'credentials')
    _authenticate_account(account, old_password)

    account.set_password(new_password)
    account.save()


def racall_password(email):
    account = models.Account.get_by_email(email, 'credentials')
    account.forget_password()
    account.save()
    tasks.send_password_recall_email(account)


def recall_password_callback(email):
    mailing.validate_email(email)
    account = models.Account.get_by_email(email, 'credentials')
    if account:
        account.generate_recall_password_token()
        tasks.send_password_recall_email(account)


def try_login(request, email, password):
    account = models.Account.get_by_email(email, 'credentials')
    _authenticate_account(account, password)
    _login(request, account)


def logout(request):
    request.session['user_id'] = None
