import unittest
import json
from unittest.mock import patch

from sqlalchemy.orm.session import Session

from planevent.core import (
    sql,
    cache,
    redisdb,
)
from planevent.accounts.models import Account


class PlaneventTest(unittest.TestCase):

    USER_ID = 0
    USER_EMAIL = 'test@example.com'
    USER_ROLE = Account.Role.ANONYMOUS
    USER_FIELDS = {}

    def setUp(self):
        self.__transaction = self.connection.begin_nested()
        sql.DBSession = Session(self.connection)

        if self.USER_ROLE != Account.Role.ANONYMOUS:
            self.session_user_patcher = patch(
                'planevent.core.views.View.get_user_dict'
            )
            mock = self.session_user_patcher.start()
            mock.return_value = dict(
                id=self.USER_ID,
                email=self.USER_EMAIL,
                role=self.USER_ROLE,
                **self.USER_FIELDS
            )

    def tearDown(self):
        sql.DBSession.close()
        self.__transaction.rollback()
        cache.flush()
        redisdb.redis_db.flushall()

        if hasattr(self, 'session_user_patcher'):
            self.session_user_patcher.stop()

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
