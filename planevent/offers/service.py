from planevent.core import redisdb
from planevent import settings

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
