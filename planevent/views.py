import json

from pyramid.response import Response
from pyramid.view import (
    view_config,
    view_defaults,
)

from sqlalchemy.exc import DBAPIError

import planevent.models as models

@view_defaults(route_name='vendor', renderer='json')
class VendorView(object):
    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        id = self.request.matchdict['id']
        return models.DBSession.query(models.Vendor).get(id)

    @view_config(request_method='POST')
    def post(self):
        return Response('post')

    @view_config(request_method='DELETE')
    def delete(self):
        return Response('delete')


@view_defaults(route_name='vendors', renderer='json')
class VendorsView(object):
    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        return models.DBSession.query(models.Vendor).all()

    @view_config(request_method='POST')
    def post(self):
        return Response('post')


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_HistoryAtlas_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

