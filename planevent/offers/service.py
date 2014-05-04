import random

from planevent.core import redisdb
from planevent import settings
from planevent.categories import service as categories_service
from planevent.offers import models

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
