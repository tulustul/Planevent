from planevent.categories.models import Category
from planevent.core import cache

CATEGORIES = 'categories'


def _fetch_and_cache_categories():
    categories = Category.query('*').all()
    cache.set(CATEGORIES, categories)
    return categories


def get_all_categories():
    categories = cache.get(CATEGORIES)

    if categories is None:
        categories = _fetch_and_cache_categories()
    else:
        categories = [Category().deserialize(cat) for cat in categories]

    return categories
