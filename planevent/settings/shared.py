from collections import namedtuple

SECRET_KEY = '_rrlq7qpzm44$i^$rorarqzec&u+0e^%669ff9l_ao$dga2ta6'

OAuthData = namedtuple(
    'OAuthData', [
        'client_id',
        'secret_key',
        'authorize_url',
        'access_token_url',
        'user_info_url',
        'scope',
        'mapper',
    ],
)

User = namedtuple(
    'User', [
        'name',
        'email',
        'password',
        'avatar',
    ]
)

OAUTH = {
    'google': OAuthData(
        client_id='892381245855.apps.googleusercontent.com',
        secret_key='vPIEZcbXzSHMJXLAG5yumzEk',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        user_info_url='https://www.googleapis.com/oauth2/v1/userinfo',
        scope=[
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ],
        mapper={
            'first_name': 'given_name',
            'last_name': 'family_name',
        }
    ),
    'facebook': OAuthData(
        client_id='1375697412694445',
        secret_key='814f154c3744d73e57228206668d66f6',
        authorize_url='https://www.facebook.com/dialog/oauth',
        access_token_url='https://graph.facebook.com/oauth/access_token',
        user_info_url='https://graph.facebook.com/me',
        scope=['email'],
        mapper={},
    ),
}

MAILGUN_PATH = 'https://api.mailgun.net/v2/sandbox45822.mailgun.org/messages'
MAILGUN_API_KEY = 'key-0tfk1t9jh842i9e72lbdf-2t44pbse55'
EMAIL_ADDRESS = 'portal@planevent.com'
PIWIK_URL = ''

GOOGLE_DOCS_LOGIN = 'planevent.export@gmail.com'
GOOGLE_DOCS_PASSWORD = 'cocojopre'

GOOGLE_IMPORT_SPREADSHET = '1x_Y5PMCjkZpc6kTMACjMBbdE0YgPW9F3Okt3pW1qmHE'
# GOOGLE_IMPORT_SPREADSHET = '0AunjHEDjOYHUdEhzTWdfcG5vNUZnYk9rRjhyVjJ5MlE'
GOOGLE_IMPORT_WORKSHEET = 'baza'

GOOGLE_EXPORT_SPREADSHET = '1i6Jtpj-55Kt1L6A4pSQ2MlqLf_FrTXDHy-XYh1qFL5g'
# GOOGLE_EXPORT_SPREADSHET = '0AunjHEDjOYHUdGU3MjdiYktOa1dxbi1XTEtMNFMtSEE'
GOOGLE_EXPORT_WORKSHEET = 'export'

RECALL_PASSWORD_TOKEN_EXPIRATION_TIME = 60  # in minutes
MINIMUM_PASSWORD_LENGTH = 5

ADMINS = [
    User(
        name='tul super admin',
        email='tulfm@poczta.fm',
        password='admin',
        avatar='/static/images/avatars/avatar_200.gif',
    ),
]

OFFER_VIEW_INCREMENT_DELAY = 5  # in minutes

USE_PERMISSIONS = True
