import unittest
import json

from pyramid.paster import get_app
from webtest import TestApp
from sqlalchemy.orm.session import Session

import planevent.models as models
from planevent.core import sql
from planevent import cache
from planevent import redisdb
import planevent


transaction = None
connection = None
app = None


def setup_module():
    global transaction, connection, app

    app = TestApp(get_app('testing.ini'))

    connection = planevent.sql_engine.connect()
    transaction = connection.begin()
    sql.Base.metadata.drop_all(connection)
    sql.Base.metadata.create_all(connection)

    redisdb.createConnections()


def teardown_module():
    global transaction, connection

    transaction.rollback()
    connection.close()


class PlaneventTest(unittest.TestCase):

    def setUp(self):
        self.__transaction = connection.begin_nested()
        sql.DBSession = Session(connection)

    def tearDown(self):
        sql.DBSession.close()
        self.__transaction.rollback()
        cache.flush()
        redisdb.redis_db.flushall()

    def get_response_data(self, response):
        return json.loads(response.body.decode())

    def get(self, *args, **kwargs):
        return self.get_response_data(app.get(*args, **kwargs))

    def post(self, *args, **kwargs):
        return self.get_response_data(app.post(*args, **kwargs))

    def put(self, *args, **kwargs):
        return self.get_response_data(app.put(*args, **kwargs))

    def delete(self, *args, **kwargs):
        return self.get_response_data(app.delete(*args, **kwargs))

    def create_vendor(self, name='test vendor', **kwargs):
        vendor = models.Vendor(name=name, **kwargs)
        vendor.save()
        return vendor

    def create_tag(self, name, references_count=0):
        tag = models.Tag(name=name, references_count=references_count)
        tag.save()
        return tag
