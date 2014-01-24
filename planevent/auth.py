import json
import datetime

from oauthlib.common import urldecode
from requests_oauthlib import OAuth2Session

from planevent import (
    settings,
    models,
)


def facebook_compliance_fix(session):

    def _compliance_fix(rrr):
        token = dict(urldecode(rrr.text))
        expires = token.get('expires')
        if expires is not None:
            token['expires_in'] = expires
        token['token_type'] = 'Bearer'
        rrr._content = bytes(json.dumps(token), encoding='utf8')
        return rrr

    session.register_compliance_hook('access_token_response', _compliance_fix)
    return session


def _get_oauth2_callback_url(request, provider):
    return request.route_url('oauth2_callback', provider=provider)


def logout(request):
    request.session['user_id'] = None
    return request.route_url('home')


def login(request, provider):
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


def process_callback(request, provider):
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

    account, is_new = process_user(provider, provider_user)

    request.session['user_id'] = account.id

    if is_new:
        return request.route_url('home') + '#/userProfile/firstLogging'
    else:
        return request.route_url('home')


def process_user(provider, provider_user):

    def fill_user_field(account, provider_user, provider_settings, field):
        provider_field = provider_settings.mapper.get(field) or field
        setattr(account, field, provider_user.get(provider_field))

    account = models.Account.query() \
        .filter(models.Account.provider==provider) \
        .filter(models.Account.origin_id==provider_user['id']) \
        .first()

    is_new = False
    if not account:
        account = models.Account(
            origin_id=provider_user['id'],
            provider=provider,
            created_at=datetime.datetime.now(),
            login_count=0,
        )
        is_new = True

    provider_settings = settings.OAUTH[provider]

    fill_user_field(account, provider_user, provider_settings, 'name')
    fill_user_field(account, provider_user, provider_settings, 'first_name')
    fill_user_field(account, provider_user, provider_settings, 'last_name')
    fill_user_field(account, provider_user, provider_settings, 'email')
    fill_user_field(account, provider_user, provider_settings, 'gender')
    fill_user_field(account, provider_user, provider_settings, 'link')

    account.last_login = datetime.datetime.now()
    account.login_count += 1

    account.save()
    return account, is_new
