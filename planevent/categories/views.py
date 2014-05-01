from planevent.core.decorators import (
    permission,
    route,
    Rest,
    Body,
)
from planevent.categories import service
from planevent.core.views import View
from planevent.categories.models import Category
from planevent import redisdb


@route('categories')
class CategoriesView(View):
    CATEGORIES_KEY = 'categories'

    def get(self):
        return service.get_all_categories('*')

    def post(self, category: Body(Category)):
        category.save()
        service._fetch_and_cache_categories()
        return category

    def delete(category_id: int):
        Category.delete(category_id)
        service._fetch_and_cache_categories()
        return self.response(200, 'category_deleted', id=category_id)
