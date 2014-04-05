import datetime

from pyramid.view import (
    view_config,
    view_defaults,
)

from planevent.offers import models
from planevent.core.decorators import (
    param,
    image_upload,
    time_profiler,
)
from planevent.services import geocode_location
from planevent.core import (
    sql,
    cache,
)
from planevent.core.views import View


VENDOR_KEY = 'vendor:{}'
CATEGORIES_KEY = 'categories'
SUBCATEGORIES_KEY = 'subcategories'


@view_defaults(route_name='vendor', renderer='json')
class VendorView(View):

    @time_profiler('VendorView')
    @view_config(request_method='GET')
    @param('id', int, required=True, rest=True)
    def get(self, id):
        vendor = cache.get((VENDOR_KEY, id), models.Vendor)
        if vendor:
            return vendor

        vendor = models.Vendor.get(id, '*')
        if not vendor:
            self.request.response.status = 404
            return {'error': 'No vendor with id ' + str(id)}
        cache.set((VENDOR_KEY, id), vendor)
        return vendor

    @view_config(request_method='DELETE')
    @param('id', int, required=True, rest=True)
    def delete(self, id):
        vendor = models.Vendor.get(id)
        if not vendor:
            self.request.response.status = 404
            return {'error': 'No vendor with id ' + str(id)}
        models.Vendor.delete(id)
        cache.delete((VENDOR_KEY, vendor.id))
        return {'message': 'deleted', 'id': id}


@view_defaults(route_name='vendor_promotion', renderer='json')
class VendorPromotionView(View):

    @view_config(request_method='POST')
    @param('id', int, required=True, rest=True)
    @param('promotion', int, required=True, rest=True)
    def post(self, id, promotion):
        vendor = models.Vendor.get(id)
        if not vendor:
            self.request.response.status = 404
            return {'error': 'No vendor with id ' + str(id)}
        vendor.promotion = promotion
        vendor.save()
        cache.set((VENDOR_KEY, vendor.id), vendor)
        return {'message': 'saved', 'id': id, 'promotion': promotion}


@view_defaults(route_name='vendors_search', renderer='json')
class SearchVendorsView(View):

    @time_profiler('SearchVendorsView')
    @view_config(request_method='GET')
    @param('category', int, default=0)
    @param('tags', list)
    @param('location', str)
    @param('range', int)
    @param('exclude_vendor_id', int)
    @param('price_min', int)
    @param('price_max', int)
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    def get(self, category, tags, location, range, exclude_vendor_id, price_min,
            price_max, offset, limit):

        query = sql.DBSession.query(models.Vendor.id)

        if category != 0:
            query = query.filter(models.Vendor.category_id == category)

        if tags:
            query = query.join(models.VendorTag) \
                .filter(models.VendorTag.tag_id.in_(tags))

        if exclude_vendor_id:
            query = query.filter(models.Vendor.id != exclude_vendor_id)

        if price_min is not None:
            query = query.filter(models.Vendor.price_min >= price_min)

        if price_max is not None:
            query = query.filter(models.Vendor.price_max <= price_max)

        if location:
            latlng = geocode_location(location)
            if latlng:
                range /= 111.12
                query = query.join(models.Address) \
                    .filter(models.Address.longitude.between(
                        latlng.lng-range, latlng.lng+range)) \
                    .filter(models.Address.latitude.between(
                        latlng.lat-range, latlng.lat+range))

        query = query.order_by(models.Vendor.promotion.desc())

        total_count = query.count()

        vendors_ids = [
            t[0] for t in query.limit(limit).offset(offset).all()
        ]

        vendors = models.Vendor.query('address', 'logo') \
            .filter(models.Vendor.id.in_(vendors_ids)).all()

        return {
            'total_count': total_count,
            'vendors': vendors,
        }


@view_defaults(route_name='vendors', renderer='json')
class VendorsView(View):

    @view_config(request_method='POST')
    @param('vendor', models.Vendor, body=True, required=True)
    def post(self, vendor):
        original_vendor = cache.get((VENDOR_KEY, vendor.id), models.Vendor)
        if not original_vendor:
            original_vendor = models.Vendor.get(vendor.id)

        if original_vendor:
            vendor.promotion = original_vendor.promotion

        now = datetime.datetime.now()
        if not vendor.added_at:
            vendor.added_at = now
        else:
            vendor.updated_at = now
        vendor.save()
        cache.set((VENDOR_KEY, vendor.id), vendor)
        return vendor


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
