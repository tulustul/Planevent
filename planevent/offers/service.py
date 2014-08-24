import random

from planevent.core import redisdb
from planevent import settings
from planevent.accounts.models import (
    Account,
    AccountLiking,
)
from planevent.categories import service as categories_service
from planevent.categories.models import Subcategory
from planevent.offers import models
from planevent.core.models import Address

VIEW_IS_SEEN = 'viewactive:{}:{}:{}'  # .format(ip, user_id, offer_id)


def increment_view_count(offer, request):
    view_is_seen_key = VIEW_IS_SEEN.format(
        request.remote_addr,
        request.session.get('user_id'),
        offer.id
    )

    view_is_seen = redisdb.redis_db.get(view_is_seen_key)

    if not view_is_seen:
        offer.increment_views_count()

    redisdb.redis_db.set(view_is_seen_key, True)
    redisdb.redis_db.expire(
        view_is_seen_key,
        settings.OFFER_VIEW_INCREMENT_DELAY * 60
    )


def _get_random_categories(categories_limit):
    categories = categories_service.get_all_categories()
    if categories_limit:
        categories = random.sample(categories, categories_limit)
    return categories


def get_promoted_offers(limit_per_category, categories_limit):
    categories = _get_random_categories(categories_limit)

    result = []
    for category in categories:
        offers = models.Offer.query('address') \
            .filter(models.Offer.category_id == category.id) \
            .order_by(models.Offer.promotion) \
            .limit(limit_per_category) \
            .all()
        result.append({
            'category': category,
            'offers': offers,
        })

    return result


def get_recomendations(limit=10):

    ids = Account.columns(Account.id)

    for account_id in ids:
        yield get_account_recomendations(account_id, limit=limit)


def get_account_recomendations(account_id, limit=10):

    def get_liking_subcategory(likings, level):
        return [
            liking.subcategory.id for liking in account.likings
            if liking.level == level
        ]

    def get_offers(subcategory_ids, recomendations_settings):
        query = (
            models.Offer.query()
            .filter(Subcategory.id.in_(subcategory_ids))
        )

        if recomendations_settings:
            lat = recomendations_settings.lat
            lon = recomendations_settings.lon
            distance = recomendations_settings.distance
            query = (
                query
                .filter(Address.longitude.between(
                    lat - distance, lon + distance
                ))
                .filter(Address.latitude.between(
                    lat - distance, lon + distance
                ))
            )

        return query.order_by(models.Offer.promotion).limit(limit).all()

    if account_id is None:
        return []

    account = Account.get(
        account_id,
        'settings',
        'settings.address',
        'likings',
        'likings.subcategory',
    )

    loves = get_liking_subcategory(account.likings, AccountLiking.Level.LOVE)
    likes = get_liking_subcategory(account.likings, AccountLiking.Level.LIKE)
    mehs = get_liking_subcategory(account.likings, AccountLiking.Level.MEH)

    settings = account.settings.recommendations

    result = get_offers(loves, settings)
    if len(result) < limit:
        result += get_offers(likes, settings)
    if len(result) < limit:
        result += get_offers(mehs, settings)

    return result
