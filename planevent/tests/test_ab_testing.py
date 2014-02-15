from collections import namedtuple
import json

from planevent.tests import PlaneventTest
from planevent.abtesting import models


class ABTestingTestCase(PlaneventTest):

    Variation = namedtuple('Variation', ['name', 'probability'])

    def crate_ab_test_dict(self, name, variations):
        experiment = {
            'name': name,
            'description': 'test description',
            'variations': [],
        }

        for var in variations:
            experiment['variations'].append(
                self.create_variation_dict(var.name, var.probability)
            )

        return experiment

    def create_variation_dict(self, name, probability):
        return {
            'name': name,
            'description': 'test description',
            'probability': probability,
        }

    def create_and_post_experiment(self, name, variations, status=200):
        return self.post_experiment(
            self.crate_ab_test_dict(name, variations),
            status=status
        )

    def post_experiment(self, experiment, status=200):
        return self.post(
            '/api/experiments',
            params=json.dumps(experiment),
            status=status
        )


class ManagingTestCase(ABTestingTestCase):

    def test_post(self):
        experiment = self.create_and_post_experiment('test2', [
            self.Variation(name='var1', probability=1),
            self.Variation(name='var2', probability=2),
        ])

        self.assertEquals(experiment['name'], 'test2')
        self.assertEquals(experiment['description'], 'test description')
        self.assertIsNotNone(experiment['created_at'])
        self.assertTrue(experiment['in_preparations'])
        self.assertFalse(experiment['active'])

        self.assertEquals(len(experiment['variations']), 2)
        self.assertEquals(experiment['variations'][0]['name'], 'var1')
        self.assertEquals(experiment['variations'][0]['probability'], 1)
        self.assertEquals(experiment['variations'][0]['receivers_count'], 0)
        self.assertEquals(experiment['variations'][0]['success_count'], 0)
        self.assertEquals(experiment['variations'][1]['name'], 'var2')
        self.assertEquals(experiment['variations'][1]['probability'], 2)

    def test_post_twice(self):
        self.create_and_post_experiment('test2', [])
        self.create_and_post_experiment('test2', [], status=409)

    def test_edit(self):
        experiment = self.create_and_post_experiment('test2', [
            self.Variation(name='var1', probability=1),
        ])

        self.assertEquals(len(experiment['variations']), 1)

        experiment['name'] = 'modified test'
        experiment['active'] = True
        # experiment['variations'].append(self.create_variation_dict('var 2', 1))

        experiment = self.post_experiment(experiment)

        self.assertEquals(experiment['name'], 'modified test')
        self.assertFalse(experiment['active'])
        self.assertEquals(len(experiment['variations']), 2)

    def test_edit_active(self):
        pass

    def test_edit_previously_activated(self):
        pass


class GettingListTestCase(ABTestingTestCase):

    def test_get_active(self):
        pass

    def test_get_active_with_offset_and_limit(self):
        pass

    def test_get_inactive(self):
        pass


class ActivationTestCase(ABTestingTestCase):

    def test_activate(self):
        pass

    def test_activate_already_active(self):
        pass

    def test_activate_not_existing(self):
        pass

    def test_deactivate(self):
        pass

    def test_deactivate_already_inactive(self):
        pass

    def test_deactivate_not_existing(self):
        pass

    def test_remove_all_redis_data_on_deactivation(self):
        pass


class VariationTestCase(ABTestingTestCase):

    def test_get_variation(self):
        pass

    def test_get_new_variation_for_user(self):
        pass

    def test_get_old_variation_for_user(self):
        pass

    def test_get_variation_for_not_existing_experiment(self):
        pass

    def test_get_variation_for_finished(self):
        pass

    def test_increment_variation(self):
        pass
