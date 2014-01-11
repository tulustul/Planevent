import unittest
import sys
import json

from pyramid.paster import get_app
from sqlalchemy import create_engine
from webtest import TestApp

import planevent.models as models

class PlaneventTest(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(get_app('testing.ini'))
        models.Base.metadata.create_all(models.DBSession.get_bind())

    def tearDown(self):
        models.DBSession.remove()

    def get_response_data(self, response):
        return json.loads(response.body.decode())

    def get(self, *args, **kwargs):
        return self.get_response_data(self.app.get(*args, **kwargs))

    def post(self, *args, **kwargs):
        return self.get_response_data(self.app.post(*args, **kwargs))

    def put(self, *args, **kwargs):
        return self.get_response_data(self.app.put(*args, **kwargs))

    def delete(self, *args, **kwargs):
        return self.get_response_data(self.app.delete(*args, **kwargs))

    def create_vendor(self, name='test vendor', **kwargs):
        vendor = models.Vendor(name=name, **kwargs)
        vendor.save()
        return vendor

    def create_tag(self, name, references_count=0):
        tag = models.Tag(name=name, references_count=references_count)
        tag.save()
        return tag