import datetime
import random

from planevent.offers import models
from planevent.accounts.models import Account
from planevent.core.decorators import (
    image_upload,
    time_profiler,
    permission,
    route,
    Rest,
    Body,
)
from planevent.services import geocode_location
from planevent.core import (
    sql,
    cache,
)
from planevent.offers import service
from planevent.core.views import View
from planevent.core.models import Address

OFFER_KEY = 'offer:{}'
CATEGORIES_KEY = 'categories'
SUBCATEGORIES_KEY = 'subcategories'


@route('offer')
class OfferView(View):

    @time_profiler('OfferView')
    def get(self, offer_id: Rest(int)):
        offer = cache.get((OFFER_KEY, offer_id), models.Offer)
        if offer is None:
            offer = models.Offer.get(offer_id, '*')
            if offer:
                cache.set((OFFER_KEY, offer_id), offer)

        if not offer:
            return self.response(404, 'No offer with id {}'.format(offer_id))

        service.increment_view_count(offer, self.request)

        return offer

    def post(self, offer_id: Rest(int), offer: Body(models.Offer)):
        original_offer = models.Offer.get(offer.id)

        if not original_offer.user_can_edit(self.get_user_dict()):
            return self.response(
                403, 'You have no permission to edit this offer'
            )

        if original_offer and offer_id == offer.id:
            offer.author = original_offer.author
            offer.added_at = original_offer.added_at
            offer.promotion = original_offer.promotion
            offer.save()
            cache.set((OFFER_KEY, offer.id), offer)
            return offer
        else:
            return self.response(404, 'No offer with id {}'.format(offer_id))


@route('offers')
class OffersView(View):

    @permission(Account.Role.NORMAL)
    def post(self, offer: Body(models.Offer)):
        if offer.id:
            return self.response(
                400, 'New offer cannot have id',
            )
        offer.added_at = datetime.datetime.now()
        offer.updated_at = now
        offer.save()
        cache.set((OFFER_KEY, offer.id), offer)
        return offer


class ChangeStatusBaseMixin(object):
    def change_status(self, offer_id, accepted_statuses, new_status):
        offer = models.Offer.get(offer_id)
        if not offer:
            return self.response(404, 'No offer with id {}'.format(id))
        elif not offer.user_can_edit(self.get_user_dict()):
            return self.response(
                403, 'You have no permission to edit this offer'
            )
        elif offer.status not in accepted_statuses:
            return self.response(409, 'Only inactive offers can be activated')
        else:
            offer.status = new_status
            offer.save()
            cache.delete((OFFER_KEY, offer.id))
            return {
                'message': 'status_changed',
                'id': offer_id,
                'status': new_status,
            }


@route('offer_activate')
class OfferView(View, ChangeStatusBaseMixin):
    @permission(Account.Role.NORMAL)
    def post(self, offer_id: Rest(int)):
        return self.change_status(
            offer_id,
            [models.Offer.Status.INACTIVE],
            models.Offer.Status.ACTIVE,
        )


@route('offer_deactivate')
class OfferView(View, ChangeStatusBaseMixin):
    @permission(Account.Role.NORMAL)
    def post(self, offer_id: Rest(int)):
        return self.change_status(
            offer_id,
            [models.Offer.Status.ACTIVE],
            models.Offer.Status.INACTIVE,
        )


@route('offer_delete')
class OfferView(View, ChangeStatusBaseMixin):
    @permission(Account.Role.NORMAL)
    def post(self, offer_id: Rest(int)):
        return self.change_status(
            offer_id,
            [models.Offer.Status.ACTIVE, models.Offer.Status.INACTIVE],
            models.Offer.Status.DELETED,
        )


@route('offer_promotion')
class OfferPromotionView(View):

    @permission(Account.Role.ADMIN)
    def post(
        self,
        offer_id: Rest(int),
        promotion: Rest(int),
    ):

        offer = models.Offer.get(offer_id)
        if not offer:
            return self.response(404, 'No offer with id {}'.format(offer_id))
        offer.promotion = promotion
        offer.save()
        cache.set((OFFER_KEY, offer.id), offer)
        return {'message': 'saved', 'id': offer_id, 'promotion': promotion}


@route('offers_search')
class SearchOffersView(View):

    @time_profiler('SearchOffersView')
    def get(
        self,
        category: int=None,
        tags: list=None,
        location: str=None,
        range: int=None,
        exclude_offer_id: int=None,
        price_min: int=None,
        price_max: int=None,
        offset: int=0,
        limit: int=10,
        active_only: bool=True,
        author_id: int=None,
    ):
        query = sql.DBSession.query(models.Offer.id)

        if category is not None:
            query = query.filter(models.Offer.category_id == category)

        if tags:
            query = query.join(models.OfferTag) \
                .filter(models.OfferTag.tag_id.in_(tags))

        if exclude_offer_id:
            query = query.filter(models.Offer.id != exclude_offer_id)

        if price_min is not None:
            query = query.filter(models.Offer.price_min >= price_min)

        if price_max is not None:
            query = query.filter(models.Offer.price_max <= price_max)

        if location and range:
            latlng = geocode_location(location)
            if latlng:
                range /= 111.12
                query = query.join(Address) \
                    .filter(Address.longitude.between(
                        latlng.lng - range, latlng.lng + range)) \
                    .filter(Address.latitude.between(
                        latlng.lat - range, latlng.lat + range))

        query = query.order_by(models.Offer.promotion.desc())

        total_count = query.count()

        offers_ids = [
            t[0] for t in query.limit(limit).offset(offset).all()
        ]

        offers = models.Offer.query('address', 'logo') \
            .filter(models.Offer.id.in_(offers_ids)).all()

        return {
            'total_count': total_count,
            'offers': offers,
        }


@route('logo')
class LogoView(View):

    @image_upload('static/images/uploads/logos/', size=(200, 200))
    def post(self, image_path):
        return {'path': image_path}


@route('gallery')
class GalleryView(View):

    @image_upload('static/images/uploads/galleries/', size=(800, 500))
    def post(self, image_path):
        return {'path': image_path}


@route('tag_autocomplete')
class TagsAutocompleteView(View):

    def get(self, tag: str=None):
        query = models.Tag.query()
            # .order_by(models.Tag.references_count.desc()) \
            # .limit(limit)
        if tag:
            query = query.filter(models.Tag.name.like('%' + tag + '%'))

        return query.all()


@route('tag_names')
class TagsNamesView(View):

    def get(self):
        query = models.Tag.query()
        # return [tag.name for tag in query.all()]
        return query.all()


@route('tags')
class TagsView(View):

    def get(self, limit: int=10, offset: int=0):
        query = models.Tag.query() \
            .order_by(models.Tag.references_count.desc()) \
            .limit(limit).offset(offset)
        return query.all()

    def post(self, tag_name: str):
        tag = models.Tag.query() \
            .filter(models.Tag.name == tag_name).first()
        if tag:
            self.request.response.status = 409
            return {
                'error': 'Tag "' + tag_name + '" already exists',
                'tag_id': tag.id,
            }

        tag = models.Tag(name=tag_name)
        tag.save()
        return tag


@route('offers_promoted')
class PromotedCategoriesOffersView(View):
    def get(self, limit_per_category: int=10, categories_limit: int=4):
        return service.get_promoted_offers(
            limit_per_category,
            categories_limit,
        )


@route('offer_recommendations')
class RecommendedOffersView(View):

    @permission(Account.Role.NORMAL)
    def get(self, limit: int=10):
        return service.get_account_recomendations(self.get_user_id())
