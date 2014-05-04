import math

from pyramid.exceptions import NotFound
from planevent.offers import models
from planevent.accounts.models import Account
from planevent.core.decorators import (
    route,
    seo_route,
    Rest,
    Template,
)
from planevent.offers import service
from planevent.core.views import View
from planevent.categories import service as categories_service


@route('seo_home')
class HomeView(View):
    def get(self) -> Template('seo/pages/index'):
        promoted_offers = service.get_promoted_offers(
            limit_per_category=10,
            categories_limit=None,
        )
        return {
            'promoted_offers': promoted_offers,
        }


@seo_route('seo_search')
class SearchView(View):
    LIMIT = 30

    def get(self, page: int=0) -> Template('seo/pages/search'):
        total_quantity = models.Offer.count()

        offers = models.Offer.query() \
            .order_by(models.Offer.promotion) \
            .limit(self.LIMIT) \
            .offset(self.LIMIT * page) \
            .all()

        return {
            'offers': offers,
            'current_page': page,
            'total_pages': math.ceil(total_quantity / self.LIMIT),
        }


@seo_route('seo_offer')
class OfferView(View):
    def get(self, id: Rest(int)) -> Template('seo/pages/offer'):
        offer = models.Offer.get(id)
        if offer is None:
            raise NotFound
        else:
            return {
                'offer': models.Offer.get(id)
            }
