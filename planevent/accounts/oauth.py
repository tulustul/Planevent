import json
import os

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes.facebook import facebook_compliance_fix

from planevent import settings
from planevent.accounts import (
    models,
    tasks,
    auth,
)

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 'True'


def _get_oauth2_callback_url(request, provider):
    return request.route_url('oauth2_callback', provider=provider)


def login_oauth(request, provider):
    provider_settings = settings.OAUTH[provider]

    oauth = OAuth2Session(
        provider_settings.client_id,
        redirect_uri=_get_oauth2_callback_url(request, provider),
        scope=provider_settings.scope,
    )

    authorization_url, state = oauth.authorization_url(
        provider_settings.authorize_url,
    )

    return authorization_url


def process_oauth_callback(request, provider):
    provider_settings = settings.OAUTH[provider]

    oauth = OAuth2Session(
        provider_settings.client_id,
        redirect_uri=_get_oauth2_callback_url(request, provider),
        state=request.params['state'],
        scope=provider_settings.scope,
    )

    if provider == 'facebook':
        oauth = facebook_compliance_fix(oauth)

    token = oauth.fetch_token(
        provider_settings.access_token_url,
        authorization_response=request.url,
        client_secret=provider_settings.secret_key,
    )

    oauth.token = token

    response = oauth.get(provider_settings.user_info_url)
    provider_user = json.loads(response.content.decode('utf8'))

    account, is_new = process_oauth_user(provider, provider_user)

    auth._login(request, account)

    if is_new:
        return request.route_url('home') + '#/userProfile/firstLogging'
    else:
        return request.route_url('home')


def process_oauth_user(provider, provider_user):

    def fill_user_fields(account, provider_user, provider_settings):
        def fill_user_field(field):
            provider_field = provider_settings.mapper.get(field) or field
            setattr(account, field, provider_user.get(provider_field))

        fill_user_field('name')
        fill_user_field('first_name')
        fill_user_field('last_name')
        fill_user_field('gender')
        fill_user_field('link')

    account = models.Account.get_by_provider(provider, provider_user['id'])

    is_new = False
    if not account:
        account = models.Account.create(email=provider_user.get('email'))
        account.credentials.origin_id = provider_user.get('id'),
        account.credentials.provider = provider,
        is_new = True

    provider_settings = settings.OAUTH[provider]

    fill_user_fields(account, provider_user, provider_settings)

    if is_new:
        tasks.send_welcome_email(account)

    return account, is_new
