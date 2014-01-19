import datetime

from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

from planevent import (
    models,
    cache,
)
from planevent.decorators import (
    param,
    image_upload,
    time_profiler,
)
from planevent.services import geocode_location
from planevent import auth


VENDOR_KEY = 'vendor:{}'


class View(object):

    def __init__(self, request):
        self.request = request


@view_config(route_name='home', renderer='../templates/index.pt')
def home_view(request):
    return {}


@view_config(route_name='admin', renderer='../templates/admin.pt')
def admin_view(request):
    return {}


@view_defaults(route_name='login_oauth2')
class LoginView(View):

    @view_config(request_method='GET')
    @param('provider', str, required=True, rest=True)
    def get(self, provider):
        return HTTPFound(location=auth.authorize(self.request, provider))


@view_defaults(route_name='oauth2_callback', renderer='json')
class OAuth2CallbackView(View):

    @view_config(request_method='GET')
    @param('provider', str, required=True, rest=True)
    def get(self, provider):
        # return HTTPFound(location=auth.process_callback(self.request, provider))
        return auth.process_callback(self.request, provider)


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
        return {'message': 'deleted', 'id': id};


@view_defaults(route_name='related_vendors', renderer='json')
class RelatedVendorsView(View):

    @view_config(request_method='GET')
    @param('id', int, required=True, rest=True)
    @param('offset', int, default=0)
    @param('limit', int, default=5)
    def get(self, id, offset, limit):
        vendor = models.Vendor.get(id, 'tags')
        if not vendor:
            self.request.response.status = 404
            return {'error': 'No vendor with id ' + str(id)}

        tags = [tag.id for tag in vendor.tags]
        query = models.Vendor.query('logo', 'address') \
                .join(models.VendorTag) \
                .filter(models.VendorTag.tag_id.in_(tags)) \
                .filter(models.Vendor.id!=id)

        query = query.order_by(models.Vendor.promotion.desc())
        return query.limit(limit).offset(offset).all()


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
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    def get(self, category, tags, location, range, exclude_vendor_id, offset,
            limit):

        query = models.DBSession.query(models.Vendor.id)

        if category != 0:
            query = query.filter(models.Vendor.category==category)

        if tags:
            query = query.join(models.VendorTag) \
                .filter(models.VendorTag.tag_id.in_(tags))

        if exclude_vendor_id:
            query = query.filter(models.Vendor.id!=exclude_vendor_id)

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

        vendors_ids = [t[0] for t in query.limit(limit).offset(offset).all()]

        return models.Vendor.query('address', 'logo') \
            .filter(models.Vendor.id.in_(vendors_ids)).all()

@view_defaults(route_name='vendors', renderer='json')
class VendorsView(View):

    @view_config(request_method='GET')
    @param('category', int, default=0)
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    def get(self, category, offset, limit):
        query = models.Vendor.query('address', 'logo')
        if category != 0:
            query = query.filter(models.Vendor.category==category)
        query = query.order_by(models.Vendor.promotion.desc())
        return query.limit(limit).offset(offset).all()

    @view_config(request_method='POST')
    @param('vendor', models.Vendor, body=True, required=True)
    def post(self, vendor):
        # TODO restore original promotion value
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
    @image_upload('static/images/uploads/logos/', size=(200,200))
    def post(self, image_path):
        return {'path': image_path}


@view_defaults(route_name='gallery', renderer='json')
class GalleryView(View):

    @view_config(request_method='POST')
    @image_upload('static/images/uploads/galleries/', size=(800,500))
    def post(self, image_path):
        return {'path': image_path}


@view_defaults(route_name='tag_autocomplete', renderer='json')
class TagsAutocompleteView(View):

    @view_config(request_method='GET')
    @param('tag', str, required=True, rest=True)
    @param('limit', int, default=10)
    def get(self, tag, limit):
        query = models.Tag.query() \
            .filter(models.Tag.name.like('%'+tag+'%')) \
            .order_by(models.Tag.references_count.desc()) \
            .limit(limit)
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
    @param('tag_name', str, body=True, required=True)
    def post(self, tag_name):
        tag = models.Tag.query() \
                .filter(models.Tag.name==tag_name).first()
        if tag:
            self.request.response.status = 409
            return {
                'error': 'Tag "' + tag_name + '" already exists',
                'tag_id': tag.id,
            }

        tag = models.Tag(name=tag_name)
        tag.save()
        return tag
