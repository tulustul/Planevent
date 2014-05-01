from planevent.categories.models import Category
from planevent.core import cache

CATEGORIES = 'categories_{}'  # .format('_'.join(relations))


def _get_categories_key(*relations):
    return CATEGORIES.format('_'.join(relations))


def _fetch_and_cache_categories(categories_key, *relations):
    categories_key = _get_categories_key(*relations)
    categories = Category.query(*relations).all()
    cache.set(categories_key, categories)
    return categories


def get_all_categories(*relations):
    categories_key = _get_categories_key(*relations)
    categories = cache.get(categories_key)

    if categories is None:
        categories = _fetch_and_cache_categories(*relations)
    else:
        categories = [Category().deserialize(cat) for cat in categories]

    return categories
