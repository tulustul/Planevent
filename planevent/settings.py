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
