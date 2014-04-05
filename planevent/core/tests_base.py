import unittest
import json

from pyramid.paster import get_app
from webtest import TestApp
from sqlalchemy.orm.session import Session

import planevent
from planevent import settings
from planevent.core import (
    sql,
    cache,
    redisdb,
)


class PlaneventTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = TestApp(get_app(settings.INI_FILE))

        cls.connection = planevent.sql_engine.connect()
        cls.transaction = cls.connection.begin()
        sql.Base.metadata.drop_all(cls.connection)
        sql.Base.metadata.create_all(cls.connection)

        redisdb.createConnections()

    @classmethod
    def tearDownClass(cls):
        cls.transaction.rollback()
        cls.connection.close()

    def setUp(self):
        self.__transaction = self.connection.begin_nested()
        sql.DBSession = Session(self.connection)

    def tearDown(self):
        sql.DBSession.close()
        self.__transaction.rollback()
        cache.flush()
        redisdb.redis_db.flushall()

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
