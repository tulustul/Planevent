import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config,
    view_defaults,
)

import planevent
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
from planevent.core import sql
from planevent import (
    auth,
    settings,
    tasks,
    migration,
)
from planevent.redisdb import redis_db
from planevent.services.mailing import InvalidEmail
from planevent.async import TaskProgressCounter
from planevent.scripts.initializedb import (
    create_test_categories,
    create_test_tags,
)


VENDOR_KEY = 'vendor:{}'
CATEGORIES_KEY = 'categories'
SUBCATEGORIES_KEY = 'subcategories'


class View(object):

    def __init__(self, request):
        self.request = request

    def response(self, code=200, message=None, **kwargs):
        self.request.response.status = code
        kwargs['message'] = message
        return kwargs


@view_config(route_name='home', renderer='../templates/index.jinja2')
def home_view(request):
    return {'PIWIK_URL': settings.PIWIK_URL}


@view_config(route_name='admin', renderer='../templates/admin.jinja2')
def admin_view(request):
    return {}


@view_defaults(route_name='register', renderer='json')
class RegisterView(View):

    @view_config(request_method='POST')
    @param('credentials', str, required=True, body=True)
    def post(self, credentials):
        email, password = credentials.split(':', 1)
        try:
            auth.register(self.request, email, password)
        except auth.EmailAlreadyTaken:
            return self.response(409, 'email_already_taken')
        except InvalidEmail:
            return self.response(400, 'invalid_email')
        except models.Account.PasswordToShort:
            return self.response(
                400,
                'password_to_short',
                mimimum_length=settings.MINIMUM_PASSWORD_LENGTH,
            )
        else:
            return self.response(201, 'account_created')


@view_defaults(route_name='login', renderer='json')
class LoginView(View):

    @view_config(request_method='POST')
    @param('credentials', str, required=True, body=True)
    def post(self, credentials):
        email, password = credentials.split(':', 1)
        try:
            auth.try_login(self.request, email, password)
        except (InvalidEmail, auth.InvalidCredentials):
            return self.response(400, 'invalid_credentials')
        else:
            return self.response(200, 'logged_in')


@view_defaults(route_name='login_oauth2')
class LoginOAuthView(View):

    @view_config(request_method='GET')
    @param('provider', str, required=True, rest=True)
    def get(self, provider):
        return HTTPFound(
            location=auth.login_oauth(self.request, provider)
        )


@view_defaults(route_name='oauth2_callback', renderer='json')
class OAuth2CallbackView(View):

    @view_config(request_method='GET')
    @param('provider', str, required=True, rest=True)
    def get(self, provider):
        return HTTPFound(
            location=auth.process_oauth_callback(self.request, provider)
        )


@view_defaults(route_name='logout', renderer='json')
class LogoutView(View):

    @view_config(request_method='POST')
    def post(self):
        auth.logout(self.request)
        return self.response(200, 'logged_out')


@view_defaults(route_name='password_recall', renderer='json')
class PasswordRecallView(View):

    @view_config(request_method='POST')
    @param('email', str, required=True, body=True)
    def post(self, email):
        try:
            auth.recall_password_callback(email)
        except InvalidEmail:
            return self.response(400, 'invalid_email')
        return self.response(200, 'mail_sent')


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
        return {'message': 'deleted', 'id': id}


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
        cache.set((VENDOR_KEY, vendor.id), vendor)
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
    @param('price_min', int)
    @param('price_max', int)
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    def get(self, category, tags, location, range, exclude_vendor_id, price_min,
            price_max, offset, limit):

        query = sql.DBSession.query(models.Vendor.id)

        if category != 0:
            query = query.filter(models.Vendor.category_id == category)

        if tags:
            query = query.join(models.VendorTag) \
                .filter(models.VendorTag.tag_id.in_(tags))

        if exclude_vendor_id:
            query = query.filter(models.Vendor.id != exclude_vendor_id)

        if price_min is not None:
            query = query.filter(models.Vendor.price_min >= price_min)

        if price_max is not None:
            query = query.filter(models.Vendor.price_max <= price_max)

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

        total_count = query.count()

        vendors_ids = [
            t[0] for t in query.limit(limit).offset(offset).all()
        ]

        vendors = models.Vendor.query('address', 'logo') \
            .filter(models.Vendor.id.in_(vendors_ids)).all()

        return {
            'total_count': total_count,
            'vendors': vendors,
        }


@view_defaults(route_name='vendors', renderer='json')
class VendorsView(View):

    @view_config(request_method='POST')
    @param('vendor', models.Vendor, body=True, required=True)
    def post(self, vendor):
        original_vendor = cache.get((VENDOR_KEY, vendor.id), models.Vendor)
        if not original_vendor:
            original_vendor = models.Vendor.get(vendor.id)

        if original_vendor:
            vendor.promotion = original_vendor.promotion

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
    @image_upload('static/images/uploads/logos/', size=(200, 200))
    def post(self, image_path):
        return {'path': image_path}


@view_defaults(route_name='gallery', renderer='json')
class GalleryView(View):

    @view_config(request_method='POST')
    @image_upload('static/images/uploads/galleries/', size=(800, 500))
    def post(self, image_path):
        return {'path': image_path}


@view_defaults(route_name='tag_autocomplete', renderer='json')
class TagsAutocompleteView(View):

    @view_config(request_method='GET')
    @param('tag', str, required=False)
    # @param('limit', int, default=10)
    def get(self, tag):
        query = models.Tag.query()
            # .order_by(models.Tag.references_count.desc()) \
            # .limit(limit)
        if tag:
            query = query.filter(models.Tag.name.like('%'+tag+'%'))

        return query.all()


@view_defaults(route_name='tag_names', renderer='json')
class TagsNamesView(View):

    @view_config(request_method='GET')
    def get(self):
        query = models.Tag.query()
        # return [tag.name for tag in query.all()]
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
    def post(self, tag_name):
        tag = models.Tag.query() \
            .filter(models.Tag.name == tag_name).first()
        if tag:
            self.request.response.status = 409
            return {
                'error': 'Tag "' + tag_name + '" already exists',
                'tag_id': tag.id,
            }

        tag = models.Tag(name=tag_name)
        tag.save()
        return tag


@view_defaults(route_name='logged_user', renderer='json')
class LoggedUserView(View):

    @view_config(request_method='GET')
    def get(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            return models.Account.get(
                user_id,
                'settings',
                'settings.address',
                'likings',
                'likings.subcategory',
            )
        return

    @view_config(request_method='POST')
    @param('account', models.Account, body=True, required=True)
    def post(self, account):
        user_id = self.request.session.get('user_id')
        if account.id != user_id:
            self.request.response.status = 401
            return {
                'error': 'Can edit only owned account'
            }

        account.save()
        return account


@view_defaults(route_name='categories', renderer='json')
class CategoriesView(View):

    @view_config(request_method='GET')
    def get(self):
        categories = cache.get(CATEGORIES_KEY)
        if categories:
            return categories

        categories = models.Category.query('subcategories').all()
        cache.set(CATEGORIES_KEY, categories)
        return categories


@view_defaults(route_name='subcategories', renderer='json')
class SubcategoriesView(View):

    @view_config(request_method='GET')
    def get(self):
        subcategories = cache.get((SUBCATEGORIES_KEY))
        if subcategories:
            return subcategories

        subcategories = models.Subcategory.query().all()
        cache.set((SUBCATEGORIES_KEY), subcategories)
        return subcategories


@view_defaults(route_name='migration', renderer='json')
class MigrationView(View):

    @view_config(request_method='GET')
    @param('spreadsheet', str)
    @param('worksheet', str)
    def export(self, spreadsheet, worksheet):
        progress_counter = TaskProgressCounter.create()

        migration.export(spreadsheet, worksheet, progress_counter)

        return {
            'message': 'Export started',
            'progress_counter': progress_counter.id,
        }

    @view_config(request_method='POST')
    @param('spreadsheet', str)
    @param('worksheet', str)
    def import_(self, spreadsheet, worksheet):
        sql.Base.metadata.drop_all(planevent.sql_engine)
        sql.Base.metadata.create_all(planevent.sql_engine)

        categories, subcategories = create_test_categories()
        tags = create_test_tags()

        progress_counter = TaskProgressCounter.create()

        migration.import_(spreadsheet, worksheet, progress_counter)

        return {
            'message': 'Export started',
            'progress_counter': progress_counter.id,
        }


@view_defaults(route_name='update_schema', renderer='json')
class UpdateSchemaView(View):

    @view_config(request_method='POST')
    def post(self):
        sql.Base.metadata.create_all(planevent.sql_engine)
        return 'Database schema updated'


@view_defaults(route_name='clear_database', renderer='json')
class ClearDatabaseView(View):

    @view_config(request_method='POST')
    def post(self):
        sql.Base.metadata.drop_all(planevent.sql_engine)
        sql.Base.metadata.create_all(planevent.sql_engine)
        redis_db.flushall()
        return 'Database cleared'


@view_defaults(route_name='generate_random_instance', renderer='json')
class GenerateRandomInstancesView(View):

    @view_config(request_method='POST')
    @param('quantity', int, body=True)
    def post(self, quantity):
        progress_counter = TaskProgressCounter.create()

        tasks.generate_random_tasks(quantity, progress_counter)

        return {
            'message': 'Random data generation started',
            'progress_counter': progress_counter.id,
        }


@view_defaults(route_name='list_incomplete', renderer='json')
class ListIncompleteView(View):

    @view_config(request_method='GET')
    def get(self):
        pass


@view_defaults(route_name='task_progress', renderer='json')
class TaskProgressView(View):

    @view_config(request_method='GET')
    @param('id', int, rest=True)
    def get(self, id):
        try:
            progress = TaskProgressCounter.get(id)
        except ValueError as e:
            self.request.response.status = 404
            return {'error': str(e)}
        else:
            return {
                'id': progress.id,
                'progress': progress.progress,
                'max': progress.max,
                'status': progress.status,
                'message': progress.message,
            }


@view_defaults(route_name='task_cancel', renderer='json')
class TaskCancelView(View):

    @view_config(request_method='POST')
    @param('id', int, rest=True)
    def post(self, id):
        try:
            TaskProgressCounter.cancel(id)
        except ValueError as e:
            self.request.response.status = 404
            return {'error': str(e)}
        else:
            return 'Task {} canceled'.format(id)
