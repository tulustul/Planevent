from planevent.tests import PlaneventTest
import planevent.models as models


class VendorViewTestCase(PlaneventTest):

    def test_get(self):
        vendor = self.create_vendor('test vendor')

        data = self.get('/api/vendor/' + str(vendor.id))

        self.assertEqual(data['name'], vendor.name)

    def test_get_not_existing(self):
        self.get('/api/vendor/12', status=404)

    def test_deletion(self):
        vendor = self.create_vendor()
        data = self.delete('/api/vendor/' + str(vendor.id))
        self.get('/api/vendor/' + str(vendor.id), status=404)

    def test_deletion_not_existing(self):
        self.delete('/api/vendor/123', status=404)


class VendorsViewTestCase(PlaneventTest):

    def setUp(self):
        super().setUp()
        self.create_vendor()

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


class RelatedVendorsTestCase(PlaneventTest):

    def test_get(self):
        pass


class ImageUploadTestCase(PlaneventTest):

    def test_image_upload(self):
        pass


class TagsTestCase(PlaneventTest):

    def setUp(self):
        super().setUp()
        self.create_tag('tag1', 5)
        self.create_tag('kajaki', 1)
        self.create_tag('rowery', 2)
        self.create_tag('kuchnia grecka', 7)
        self.create_tag('kuchnia polska', 0)
        self.create_tag('kuchnia francuska', 3)

    def test_get(self):
        data = self.get('/api/tags')

        self.assertEqual(len(data), 6)

    def test_get_with_offset_and_limit(self):
        data = self.get('/api/tags', params={
                'offset': 2,
                'limit': 3,
            })
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'kuchnia francuska')
        self.assertEqual(data[1]['name'], 'rowery')
        self.assertEqual(data[2]['name'], 'kajaki')

    def test_creation(self):
        data = self.post('/api/tags', params='new tag')

        self.assertEqual(data['name'], 'new tag')

    def test_creation_already_existing(self):
        self.post('/api/tags', params='tag1', status=409)

    def test_autocomplete(self):
        data = self.get('/api/tags/autocomplete/uchnia')

        self.assertEqual(len(data), 3)

        tags_names = [tag['name'] for tag in data]

        self.assertIn('kuchnia grecka', tags_names)
        self.assertIn('kuchnia polska', tags_names)
        self.assertIn('kuchnia francuska', tags_names)
