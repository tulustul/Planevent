import datetime

from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults,
)

import planevent.models as models
from planevent.decorators import (
    param,
    image_upload
)

class View(object):

    def __init__(self, request):
        self.request = request


@view_config(route_name='home', renderer='../templates/newDesign.pt')
def home_view(request):
    return {}


@view_defaults(route_name='vendor', renderer='json')
class VendorView(View):

    @view_config(request_method='GET')
    @param('id', int, required=True, rest=True)
    def get(self, id_):
        vendor = models.Vendor.get(id_, '*')
        if not vendor:
            self.request.response.status = 404
            return {'error': 'No vendor with id ' + str(id_)}
        return vendor

    @view_config(request_method='DELETE')
    @param('id', int, required=True, rest=True)
    def delete(self, id_):
        vendor = models.Vendor.get(id_)
        if not vendor:
            self.request.response.status = 404
            return {'error': 'No vendor with id ' + str(id_)}
        models.Vendor.delete(id_)
        return {'message': 'deleted', 'id': id_};


@view_defaults(route_name='related_vendors', renderer='json')
class RelatedVendorsView(View):

    @view_config(request_method='GET')
    @param('id', int, required=True, rest=True)
    def get(self, id_):
        vendor = models.Vendor.get(id_, 'tags')
        if not vendor:
            self.request.response.status = 404
            return {'error': 'No vendor with id ' + str(id_)}

        tags = [tag.id for tag in vendor.tags]
        query = models.Vendor.query().join(models.VendorTag) \
                .filter(models.VendorTag.tag_id.in_(tags)) \
                .filter(models.Vendor.id!=id_)
        return query.all()


@view_defaults(route_name='vendors', renderer='json')
class VendorsView(View):

    @view_config(request_method='GET')
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    @param('category', int, default=0)
    def get(self, category, limit, offset):
        query = models.Vendor.query('address', 'logo')
        if category != 0:
            query = query.filter(models.Vendor.category==category)
        return query.limit(limit).offset(offset).all()

    @view_config(request_method='POST')
    @param('vendor', models.Vendor, body=True, required=True)
    def post(self, vendor):
        now = datetime.datetime.now()
        if not vendor.added_at:
            vendor.added_at = now
        else:
            vendor.updated_at = now
        vendor.save()
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
    @param('limit', int, default=10)
    @param('tag', str, required=True, rest=True)
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
    def get(self, offset, limit):
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

