import datetime

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


VENDOR_KEY = 'offer:{}'
CATEGORIES_KEY = 'categories'
SUBCATEGORIES_KEY = 'subcategories'


@route('offer')
class OfferView(View):

    @time_profiler('OfferView')
    def get(self, id: Rest(int)):
        offer = cache.get((VENDOR_KEY, id), models.Offer)
        if offer is None:
            offer = models.Offer.get(id, '*')
            if offer:
                cache.set((VENDOR_KEY, id), offer)

        if not offer:
            return self.response(404, 'No offer with id {}'.format(id))

        service.increment_view_count(offer, self.request)

        return offer

    def delete(self, id: Rest(int)):
        offer = models.Offer.get(id)
        if not offer:
            return self.response(404, 'No offer with id {}'.format(id))
        models.Offer.delete(id)
        cache.delete((VENDOR_KEY, offer.id))
        return {'message': 'deleted', 'id': id}


@route('offer_promotion')
class OfferPromotionView(View):

    @permission(Account.Role.ADMIN)
    def post(
        self,
        id: Rest(int),
        promotion: Rest(int),
    ):

        offer = models.Offer.get(id)
        if not offer:
            return self.response(404, 'No offer with id {}'.format(id))
        offer.promotion = promotion
        offer.save()
        cache.set((VENDOR_KEY, offer.id), offer)
        return {'message': 'saved', 'id': id, 'promotion': promotion}


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

        if location:
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


@route('offers')
class OffersView(View):

    def post(self, offer: Body(models.Offer)):
        original_offer = cache.get((VENDOR_KEY, offer.id), models.Offer)
        if not original_offer:
            original_offer = models.Offer.get(offer.id)

        if original_offer:
            offer.promotion = original_offer.promotion

        now = datetime.datetime.now()
        if not offer.added_at:
            offer.added_at = now
        else:
            offer.updated_at = now
        offer.save()
        cache.set((VENDOR_KEY, offer.id), offer)
        return offer


@route('image')
class ImageView(View):

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

    def get(self, limit_per_category: int=8, categories_limit: int=4):
        # user_dict = self.get_user_dict()

        # if user_dict:
        #     categories = self.getRandomLikedCategories(
        #         user_dict,
        #         categories_limit
        #     )
        # else:
        categories = self.getRandomCategories(categories_limit)

        result = {}
        for category in categories:
            result[category.name] = models.Offer.query() \
                .filter(models.Offer.category_id == category.id) \
                .order_by(models.Offer.promotion)

        return result
