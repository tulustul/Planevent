from pyramid.view import (
    view_config,
    view_defaults,
)

import planevent
from planevent.core.views import View
from planevent.accounts.models import Account
from planevent.core.decorators import (
    param,
    permission,
)
from planevent.core import sql
from planevent.core.redisdb import redis_db
from planevent.async import TaskProgressCounter
from planevent.scripts.initializedb import (
    create_test_categories,
    # create_test_tags,
)
from planevent.migrations import tasks


@view_defaults(route_name='migration', renderer='json')
class MigrationView(View):

    @view_config(request_method='GET')
    @permission(Account.Role.ADMIN)
    @param('spreadsheet', str)
    @param('worksheet', str)
    def export(self, spreadsheet, worksheet):
        progress_counter = TaskProgressCounter.create()

        tasks.export(spreadsheet, worksheet, progress_counter)

        return {
            'message': 'Export started',
            'progress_counter': progress_counter.id,
        }

    @view_config(request_method='POST')
    @permission(Account.Role.ADMIN)
    @param('spreadsheet', str)
    @param('worksheet', str)
    def import_(self, spreadsheet, worksheet):
        sql.Base.metadata.drop_all(planevent.sql_engine)
        sql.Base.metadata.create_all(planevent.sql_engine)

        categories, subcategories = create_test_categories()
        # tags = create_test_tags()

        progress_counter = TaskProgressCounter.create()

        tasks.import_(spreadsheet, worksheet, progress_counter)

        return {
            'message': 'Export started',
            'progress_counter': progress_counter.id,
        }


@view_defaults(route_name='update_schema', renderer='json')
class UpdateSchemaView(View):

    @view_config(request_method='POST')
    @permission(Account.Role.ADMIN)
    def post(self):
        sql.Base.metadata.create_all(planevent.sql_engine)
        return 'Database schema updated'


@view_defaults(route_name='clear_database', renderer='json')
class ClearDatabaseView(View):

    @view_config(request_method='POST')
    @permission(Account.Role.ADMIN)
    def post(self):
        sql.Base.metadata.drop_all(planevent.sql_engine)
        sql.Base.metadata.create_all(planevent.sql_engine)
        redis_db.flushall()
        return 'Database cleared'


@view_defaults(route_name='generate_random_instance', renderer='json')
class GenerateRandomInstancesView(View):

    @view_config(request_method='POST')
    @permission(Account.Role.ADMIN)
    @param('quantity', int, body=True)
    def post(self, quantity):
        progress_counter = TaskProgressCounter.create()

        tasks.generate_random_tasks(quantity, progress_counter)

        return {
            'message': 'Random data generation started',
            'progress_counter': progress_counter.id,
        }
