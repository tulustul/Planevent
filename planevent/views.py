import datetime

from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults,
)

import planevent.models as models
from planevent.decorators import param

class View(object):

    def __init__(self, request):
        self.request = request


@view_config(route_name='home', renderer='../templates/index.pt')
def home_view(request):
    return {}


@view_defaults(route_name='vendor', renderer='json')
class VendorView(View):

    @view_config(request_method='GET')
    @param('id', int, required=True, rest=True)
    def get(self, id_):
        return models.Vendor.get(id_)

    @view_config(request_method='DELETE')
    def delete(self):
        return Response('delete')


@view_defaults(route_name='vendors', renderer='json')
class VendorsView(View):

    @view_config(request_method='GET')
    @param('offset', int, required=True)
    @param('limit', int, required=True)
    def get(self, limit, offset):
        return models.Vendor.query()\
            .limit(limit)\
            .offset(offset)\
            .all()

    @view_config(request_method='POST')
    @param('vendor', models.Vendor, required=True)
    def post(self, vendor):
        now = datetime.datetime.now()
        if not vendor.added_at:
            vendor.added_at = now
        else:
            vendor.updated_at = now
        vendor.save()
        return Response(['saved', {'id': vendor.id}])
