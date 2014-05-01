from pyramid.exceptions import NotFound
from planevent.offers import models
from planevent.accounts.models import Account
from planevent.core.decorators import (
    seo_route,
    Rest,
    Template,
)
from planevent.offers import service
from planevent.core.views import View
from planevent.categories import service as categories_service


@seo_route('seo_offer')
class OfferView(View):

    def get(self, id: Rest(int)) -> Template('seo/offer'):
        offer = models.Offer.get(id)
        if offer is None:
            raise NotFound
        else:
            return {
                'offer': models.Offer.get(id)
            }
