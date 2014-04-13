from datetime import datetime
from unittest.mock import patch

from planevent.core.tests_base import PlaneventTest
from planevent.accounts.models import Account

TEST_EMAIL = 'test@example.com'
TEST_PASSWORD = 'password'

INVALID_EMAIL = 'invalid@email'


class RegisterTestCase(PlaneventTest):

    def test_create_account(self):
        self.post(
            '/api/register',
            '{}:{}'.format(TEST_EMAIL, TEST_PASSWORD)
        )

        account = Account.get_by_email(TEST_EMAIL)

        self.assertIsNotNone(account)
        self.assertEquals(account.email, TEST_EMAIL)
        self.assertEquals(account.first_name, 'test')

    def test_create_with_same_email(self):
        Account.create(email=TEST_EMAIL).save()

        self.post(
            '/api/register',
            '{}:{}'.format(TEST_EMAIL, TEST_PASSWORD),
            status=409,
        )

    def test_invalid_email(self):
        self.post(
            '/api/register',
            '{}:{}'.format(INVALID_EMAIL, TEST_PASSWORD),
            status=400,
        )

        account = Account.get_by_email(INVALID_EMAIL)
        self.assertIsNone(account)

    def test_too_short_password(self):
        self.post(
            '/api/register',
            '{}:{}'.format(TEST_EMAIL, 'a'),
            status=400,
        )

        account = Account.get_by_email(TEST_EMAIL)
        self.assertIsNone(account)

    def test_invalid_body(self):
        result = self.post(
            '/api/register', 'invalid_body',
            status=400,
        )

        self.assertEquals(result['message'], 'invalid_body')


class LoginTestCase(PlaneventTest):

    def setUp(self):
        super().setUp()

        account = Account.create(email=TEST_EMAIL)
        account.set_password(TEST_PASSWORD)
        account.save()

    def test_login(self):
        account = self.post(
            '/api/login',
            '{}:{}'.format(TEST_EMAIL, TEST_PASSWORD)
        )

        self.assertIsNotNone(account)
        self.assertEquals(account['email'], TEST_EMAIL)

    def test_invalid_email(self):
        result = self.post(
            '/api/login',
            '{}:{}'.format('test2@example.com', TEST_PASSWORD),
            status=400
        )

        self.assertEquals(result['message'], 'invalid_credentials')

    def test_invalid_password(self):
        result = self.post(
            '/api/login',
            '{}:{}'.format(TEST_EMAIL, 'invalid_password'),
            status=400
        )

        self.assertEquals(result['message'], 'invalid_credentials')


class PasswordRecallTestCase(PlaneventTest):

    @patch('planevent.accounts.tasks.send_password_recall_email')
    def test_send_mail_with_token(self, send_email_mock):
        account = Account.create(email=TEST_EMAIL)
        account.save()

        self.post('/api/recall_password', TEST_EMAIL)

        send_email_mock.assert_called_once_with(account)

    @patch('planevent.accounts.tasks.send_password_recall_email')
    def test_send_to_not_existing_Account(self, send_email_mock):
        self.post('/api/recall_password', TEST_EMAIL)
        self.assertFalse(send_email_mock.called)

    def test_send_to_invalid_email(self):
        self.post('/api/recall_password', INVALID_EMAIL, status=400)


class PasswordRecallCallbackTestCase(PlaneventTest):

    RECALL_TOKEN = 'recall_token'

    def create_account_with_recall_token(self):
        account = Account.create(email=TEST_EMAIL)
        account.credentials.recall_token = self.RECALL_TOKEN
        account.credentials.recall_token_expiry = datetime(2014, 1, 1)
        account.save()
        return account.id

    @patch('planevent.accounts.auth.datetime')
    def test_change_password(self, datetime_mock):
        datetime_mock.now.return_value = datetime(2014, 1, 1)

        account_id = self.create_account_with_recall_token()

        result = self.post(
            '/api/recall_password_callback',
            '{}:{}'.format(self.RECALL_TOKEN, TEST_PASSWORD)
        )

        self.assertEquals(result['message'], 'password_set')

        account = Account.get(account_id)

        self.assertTrue(account.check_password(TEST_PASSWORD))
        self.assertIsNone(account.credentials.recall_token)
        self.assertIsNone(account.credentials.recall_token_expiry)

    def test_invalid_token(self):
        result = self.post(
            '/api/recall_password_callback',
            '{}:{}'.format('invalid_token', TEST_PASSWORD),
            status=400
        )

        self.assertEquals(result['message'], 'invalid_token')

    @patch('planevent.accounts.auth.datetime')
    def test_token_expired(self, datetime_mock):
        datetime_mock.now.return_value = datetime(2016, 1, 1)

        self.create_account_with_recall_token()

        result = self.post(
            '/api/recall_password_callback',
            '{}:{}'.format(self.RECALL_TOKEN, TEST_PASSWORD),
            status=400
        )

        self.assertEquals(result['message'], 'token_expired')

    @patch('planevent.accounts.auth.datetime')
    def test_password_too_short(self, datetime_mock):
        datetime_mock.now.return_value = datetime(2014, 1, 1)

        self.create_account_with_recall_token()

        result = self.post(
            '/api/recall_password_callback',
            '{}:{}'.format(self.RECALL_TOKEN, 'a'),
            status=400
        )

        self.assertTrue('password_to_short' in result['message'])


class ChangePasswordTestCase(PlaneventTest):

    USER_ROLE = Account.Role.NORMAL
    USER_EMAIL = TEST_EMAIL

    NEW_PASSWORD = 'new_password'

    def test_change_password(self):

        account = Account.create(email=TEST_EMAIL)
        account.set_password(TEST_PASSWORD)
        account.save()

        result = self.post(
            '/api/change_password',
            '{}:{}'.format(TEST_PASSWORD, self.NEW_PASSWORD)
        )

        self.assertEquals(result['message'], 'password_changed')

        modified_account = Account.get(account.id)

        self.assertTrue(modified_account.check_password(self.NEW_PASSWORD))

    def test_invalid_credentials(self):
        result = self.post(
            '/api/change_password',
            '{}:{}:{}'.format(INVALID_EMAIL, TEST_PASSWORD, self.NEW_PASSWORD),
            status=400,
        )

        self.assertEquals(result['message'], 'invalid_credentials')

    def test_invalid_body(self):

        result = self.post(
            '/api/change_password',
            'invalid_body',
            status=400,
        )

        self.assertEquals(result['message'], 'invalid_body')
