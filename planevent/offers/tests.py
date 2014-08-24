from planevent.core.tests_base import PlaneventTest
from planevent.accounts.models import (
    Account,
    AccountLiking,
)
from planevent.categories.models import (
    Category,
    Subcategory,
)
from planevent.offers import (
    models,
    service,
)


class OffersBaseTestCase(PlaneventTest):

    def create_offer(self, name='test offer', **kwargs):
        offer = models.Offer(name=name, **kwargs)
        offer.save()
        return offer

    def create_tag(self, name, references_count=0):
        tag = models.Tag(name=name, references_count=references_count)
        tag.save()
        return tag


class OfferViewTestCase(OffersBaseTestCase):

    def test_get(self):
        offer = self.create_offer('test offer')

        data = self.get('/api/offer/' + str(offer.id))

        self.assertEqual(data['name'], offer.name)

    def test_get_not_existing(self):
        self.get('/api/offer/12', status=404)

    def test_deletion(self):
        offer = self.create_offer()
        self.delete('/api/offer/' + str(offer.id))
        self.get('/api/offer/' + str(offer.id), status=404)

    def test_deletion_not_existing(self):
        self.delete('/api/offer/123', status=404)


class OffersViewTestCase(OffersBaseTestCase):

    def setUp(self):
        super().setUp()
        self.create_offer()

    def get_default(self):
        pass

    def get_by_category(self):
        pass

    def get_all(self):
        pass

    def get_with_offset_and_limit(self):
        pass

    def get_creation(self):
        pass

    def get_update(self):
        pass


class RelatedOffersTestCase(OffersBaseTestCase):

    def test_get(self):
        pass


class ImageUploadTestCase(OffersBaseTestCase):

    def test_image_upload(self):
        pass


# class TagsTestCase(OffersBaseTestCase):

#     def setUp(self):
#         super().setUp()
#         self.create_tag('tag1', 5)
#         self.create_tag('kajaki', 1)
#         self.create_tag('rowery', 2)
#         self.create_tag('kuchnia grecka', 7)
#         self.create_tag('kuchnia polska', 0)
#         self.create_tag('kuchnia francuska', 3)

#     def test_get(self):
#         data = self.get('/api/tags')

#         self.assertEqual(len(data), 6)

#     def test_get_with_offset_and_limit(self):
#         data = self.get('/api/tags', params={
#             'offset': 2,
#             'limit': 3,
#         })
#         self.assertEqual(len(data), 3)
#         self.assertEqual(data[0]['name'], 'kuchnia francuska')
#         self.assertEqual(data[1]['name'], 'rowery')
#         self.assertEqual(data[2]['name'], 'kajaki')

#     def test_creation(self):
#         data = self.post('/api/tags', params='new tag')

#         self.assertEqual(data['name'], 'new tag')

#     def test_creation_already_existing(self):
#         self.post('/api/tags', params='tag1', status=409)

#     def test_autocomplete(self):
#         data = self.get('/api/tags/autocomplete/uchnia')

#         self.assertEqual(len(data), 3)

#         tags_names = [tag['name'] for tag in data]

#         self.assertIn('kuchnia grecka', tags_names)
#         self.assertIn('kuchnia polska', tags_names)
#         self.assertIn('kuchnia francuska', tags_names)


class RecomendationsTestCase(OffersBaseTestCase):

    def test_image_upload(self):
        Category(
            name='test category',
            color='FFFFFF',
            subcategories=[
                Subcategory(name='test subcategory 1', color='FFFFFF'),
                Subcategory(name='test subcategory 2', color='FFFFFF'),
            ],
        ).save()

        Account.create(email='fake_account 1')
        Account.create(email='fake_account 2')

        service.get_recomendations()
