from collections import namedtuple
import json

from planevent.core.tests_base import PlaneventTest
from planevent.abtesting import (
    models,
    service,
)
from planevent.accounts.models import Account


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

    USER_ROLE = Account.Role.ADMIN

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
        experiment['variations'].append(self.create_variation_dict('var 2', 1))

        experiment = self.post_experiment(experiment)

        self.assertEquals(experiment['name'], 'modified test')
        self.assertFalse(experiment['active'])
        self.assertEquals(len(experiment['variations']), 2)

    def test_edit_active(self):
        experiment = models.Experiment(name='test', active=True)
        experiment.save()

        experiment_dict = experiment.serialize()

        self.post_experiment(experiment_dict, status=409)

    def test_edit_previously_activated(self):
        experiment = models.Experiment(
            name='test',
            active=False,
            in_preparations=False
        )
        experiment.save()

        experiment_dict = experiment.serialize()

        self.post_experiment(experiment_dict, status=409)


class GettingListTestCase(ABTestingTestCase):

    USER_ROLE = Account.Role.ADMIN

    def setUp(self):
        super().setUp()
        self.create_and_post_experiment('test1', [
            self.Variation(name='var1_1', probability=1),
        ])
        self.create_and_post_experiment('test2', [
            self.Variation(name='var2_1', probability=1),
        ])
        self.create_and_post_experiment('test3', [
            self.Variation(name='var3_1', probability=1),
        ])
        self.get('/api/experiment/test3/activate')

    def test_get_inactive(self):
        experiments = self.get('/api/experiments', params={'active': 0})

        self.assertEquals(len(experiments), 2)

    def test_get_inactive_with_offset_and_limit(self):
        experiments = self.get('/api/experiments', params={
            'active': 0,
            'offset': 1,
            'limit': 1,
        })

        self.assertEquals(len(experiments), 1)

    def test_get_active(self):
        experiments = self.get('/api/experiments', params={'active': 1})

        self.assertEquals(len(experiments), 1)
        self.assertEquals(experiments[0]['name'], 'test3')

    def test_get_all(self):
        pass


class ActivationTestCase(ABTestingTestCase):

    USER_ROLE = Account.Role.ADMIN

    def setUp(self):
        super().setUp()
        self.create_and_post_experiment('test1', [
            self.Variation(name='var1_1', probability=1),
        ])

    def test_activate(self):
        self.get('/api/experiment/test1/activate')

    def test_activate_already_active(self):
        self.get('/api/experiment/test1/activate')
        self.get('/api/experiment/test1/activate', status=400)

    def test_activate_not_existing(self):
        self.get('/api/experiment/test2/activate', status=400)

    def test_deactivate(self):
        self.get('/api/experiment/test1/activate')
        self.get('/api/experiment/test1/deactivate')

    def test_deactivate_already_inactive(self):
        self.get('/api/experiment/test1/deactivate', status=400)

    def test_deactivate_not_existing(self):
        self.get('/api/experiment/test2/deactivate', status=400)

    def test_remove_all_redis_data_on_deactivation(self):
        pass


class VariationTestCase(ABTestingTestCase):

    USER_ROLE = Account.Role.ADMIN

    def setUp(self):
        super().setUp()
        self.create_and_post_experiment('test1', [
            self.Variation(name='var1', probability=1),
            self.Variation(name='var2', probability=2),
        ])
        self.get('/api/experiment/test1/activate')

    def test_get_variation(self):
        variation = self.get('/api/experiment/test1/variation')
        self.assertIn(variation, ['var1', 'var2'])

    def test_get_new_variation_for_user(self):
        pass

    def test_get_old_variation_for_user(self):
        pass

    def test_get_variation_for_not_existing_experiment(self):
        self.get('/api/experiment/test2/variation', status=400)

    def test_get_variation_for_finished(self):
        self.get('/api/experiment/test1/deactivate')

    def test_increment_variation(self):
        self.get('/api/experiment/test1/var1/increment')

    def test_winner_selection(self):
        self.get('/api/experiment/test1/var1/increment')
        self.get('/api/experiment/test1/var2/increment')
        self.get('/api/experiment/test1/var1/increment')

        self.get('/api/experiment/test1/deactivate')

        winner = service.get_winner('test1')

        self.assertEquals(winner, 'var1')

    def test_get_winner(self):
        variation = self.get('/api/experiment/test1/variation')

        self.get('/api/experiment/test1/{}/increment'.format(variation))

        self.get('/api/experiment/test1/deactivate')

        winner = self.get('/api/experiment/test1/variation')

        self.assertEquals(variation, winner)
