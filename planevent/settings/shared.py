from collections import namedtuple

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
        authorize_url='https://graph.facebook.com/oauth/authorize',
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

GOOGLE_IMPORT_SPREADSHET = '0AunjHEDjOYHUdEhzTWdfcG5vNUZnYk9rRjhyVjJ5MlE'
GOOGLE_IMPORT_WORKSHEET = 'baza'

GOOGLE_EXPORT_SPREADSHET = '0AunjHEDjOYHUdGU3MjdiYktOa1dxbi1XTEtMNFMtSEE'
GOOGLE_EXPORT_WORKSHEET = 'export'
