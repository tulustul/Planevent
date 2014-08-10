import planevent
from planevent.accounts.models import Account
from planevent.core.decorators import (
    permission,
    route,
    Body,
)
from planevent.core.views import View
from planevent.core import sql
from planevent.core import cache
from planevent.core.redisdb import redis_db
from planevent.async import TaskProgressCounter
from planevent.scripts.initializedb import create_test_categories
from planevent.migrations import tasks


@route('migration_export')
class MigrationExportView(View):

    @permission(Account.Role.ADMIN)
    def post(self, spreadsheet: str, worksheet: str):
        progress_counter = TaskProgressCounter.create()

        tasks.export(spreadsheet, worksheet, progress_counter)

        return {
            'message': 'Export started',
            'progress_counter': progress_counter.id,
        }


@route('migration_import')
class MigrationImportView(View):

    @permission(Account.Role.ADMIN)
    def post(self, spreadsheet: str, worksheet: str):
        sql.Base.metadata.drop_all(planevent.sql_engine)
        sql.Base.metadata.create_all(planevent.sql_engine)
        cache.flush()

        categories, subcategories = create_test_categories()
        # tags = create_test_tags()

        progress_counter = TaskProgressCounter.create()

        tasks.import_(spreadsheet, worksheet, progress_counter)
        return {
            'message': 'Export started',
            'progress_counter': progress_counter.id,
        }


@route('update_schema')
class UpdateSchemaView(View):

    @permission(Account.Role.ADMIN)
    def post(self):
        sql.Base.metadata.create_all(planevent.sql_engine)
        return 'Database schema updated'


@route('clear_database')
class ClearDatabaseView(View):

    @permission(Account.Role.ADMIN)
    def post(self):
        sql.Base.metadata.drop_all(planevent.sql_engine)
        sql.Base.metadata.create_all(planevent.sql_engine)
        redis_db.flushall()
        cache.flush()
        return 'Database cleared'


@route('generate_random_instance')
class GenerateRandomInstancesView(View):

    # @permission(Account.Role.ADMIN)
    def post(self, quantity: Body(int)):
        cache.flush()

        progress_counter = TaskProgressCounter.create()

        tasks.generate_random_tasks(quantity, progress_counter)

        return {
            'message': 'Random data generation started',
            'progress_counter': progress_counter.id,
        }
