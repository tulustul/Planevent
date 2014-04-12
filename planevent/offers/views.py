import datetime

from pyramid.view import (
    view_config,
    view_defaults,
)

from planevent.offers import models
from planevent.accounts.models import Account
from planevent.core.decorators import (
    param,
    image_upload,
    time_profiler,
    permission,
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


@view_defaults(route_name='offer', renderer='json')
class OfferView(View):

    @time_profiler('OfferView')
    @view_config(request_method='GET')
    @param('id', int, required=True, rest=True)
    def get(self, id):
        offer = cache.get((VENDOR_KEY, id), models.Offer)
        if offer is None:
            offer = models.Offer.get(id, '*')
            if offer:
                cache.set((VENDOR_KEY, id), offer)

        if not offer:
            return self.response(404, 'No offer with id {}'.format(id))

        service.increment_view_count(offer, self.request)

        return offer

    @view_config(request_method='DELETE')
    @param('id', int, required=True, rest=True)
    def delete(self, id):
        offer = models.Offer.get(id)
        if not offer:
            return self.response(404, 'No offer with id {}'.format(id))
        models.Offer.delete(id)
        cache.delete((VENDOR_KEY, offer.id))
        return {'message': 'deleted', 'id': id}


@view_defaults(route_name='offer_promotion', renderer='json')
class OfferPromotionView(View):

    @view_config(request_method='POST')
    @permission(Account.Role.ADMIN)
    @param('id', int, required=True, rest=True)
    @param('promotion', int, required=True, rest=True)
    def post(self, id, promotion):
        offer = models.Offer.get(id)
        if not offer:
            return self.response(404, 'No offer with id {}'.format(id))
        offer.promotion = promotion
        offer.save()
        cache.set((VENDOR_KEY, offer.id), offer)
        return {'message': 'saved', 'id': id, 'promotion': promotion}


@view_defaults(route_name='offers_search', renderer='json')
class SearchOffersView(View):

    @time_profiler('SearchOffersView')
    @view_config(request_method='GET')
    @param('category', str, default=0)
    @param('tags', list)
    @param('location', str)
    @param('range', int)
    @param('exclude_offer_id', int)
    @param('price_min', int)
    @param('price_max', int)
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    def get(self, category, tags, location, range, exclude_offer_id, price_min,
            price_max, offset, limit):

        query = sql.DBSession.query(models.Offer.id)

        if category is not None:
            if ',' in category:
                categories = [int(c) for c in category.split(',')]
                query = query.filter(models.Offer.category_id in categories)
            else:
                category = int(category)
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
                        latlng.lng-range, latlng.lng+range)) \
                    .filter(Address.latitude.between(
                        latlng.lat-range, latlng.lat+range))

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


@view_defaults(route_name='offers', renderer='json')
class OffersView(View):

    @view_config(request_method='POST')
    @param('offer', models.Offer, body=True, required=True)
    def post(self, offer):
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


@view_defaults(route_name='image', renderer='json')
class ImageView(View):

    @view_config(request_method='POST')
    @image_upload('static/images/uploads/logos/', size=(200, 200))
    def post(self, image_path):
        return {'path': image_path}


@view_defaults(route_name='gallery', renderer='json')
class GalleryView(View):

    @view_config(request_method='POST')
    @image_upload('static/images/uploads/galleries/', size=(800, 500))
    def post(self, image_path):
        return {'path': image_path}


@view_defaults(route_name='tag_autocomplete', renderer='json')
class TagsAutocompleteView(View):

    @view_config(request_method='GET')
    @param('tag', str, required=False)
    # @param('limit', int, default=10)
    def get(self, tag):
        query = models.Tag.query()
            # .order_by(models.Tag.references_count.desc()) \
            # .limit(limit)
        if tag:
            query = query.filter(models.Tag.name.like('%'+tag+'%'))

        return query.all()


@view_defaults(route_name='tag_names', renderer='json')
class TagsNamesView(View):

    @view_config(request_method='GET')
    def get(self):
        query = models.Tag.query()
        # return [tag.name for tag in query.all()]
        return query.all()


@view_defaults(route_name='tags', renderer='json')
class TagsView(View):

    @view_config(request_method='GET')
    @param('limit', int, default=10)
    @param('offset', int, default=0)
    def get(self, limit, offset):
        query = models.Tag.query() \
            .order_by(models.Tag.references_count.desc()) \
            .limit(limit).offset(offset)
        return query.all()

    @view_config(request_method='POST')
    def post(self, tag_name):
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


@view_defaults(route_name='categories', renderer='json')
class CategoriesView(View):

    @view_config(request_method='GET')
    def get(self):
        categories = cache.get(CATEGORIES_KEY)
        if categories:
            return categories

        categories = models.Category.query('subcategories').all()
        cache.set(CATEGORIES_KEY, categories)
        return categories


@view_defaults(route_name='subcategories', renderer='json')
class SubcategoriesView(View):

    @view_config(request_method='GET')
    def get(self):
        subcategories = cache.get((SUBCATEGORIES_KEY))
        if subcategories:
            return subcategories

        subcategories = models.Subcategory.query().all()
        cache.set((SUBCATEGORIES_KEY), subcategories)
        return subcategories
