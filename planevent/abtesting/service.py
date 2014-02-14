import json
from datetime import datetime
import random

from planevent.redisdb import redis_db
from planevent.abtesting.models import Experiment

EXPERIMENT_PATTERN = 'experiment:{}'
PROBABILITIES = EXPERIMENT_PATTERN + ':probabilities'
USER_VARIATION = EXPERIMENT_PATTERN + ':{}:user_variation'
SUCCESS_COUNT = EXPERIMENT_PATTERN + ':{}:success_count'
RECEIVERS_COUNT = EXPERIMENT_PATTERN + ':{}:receivers_count'


class ABExperimentError(Exception):
    pass


def _get_experiment(experiment_name):
    experiment = Experiment.query('variations') \
        .filter(Experiment.name == experiment_name) \
        .first()

    if experiment is None:
        raise ABExperimentError('No experiment with name ' + experiment_name)

    return experiment


def get_variation(experiment_name, user_id=None):
    def roulette(probabilities):
        rand = random.random() * sum(probabilities.values())
        roulette_pos = 0
        for variation, prob in probabilities.items():
            roulette_pos += prob
            if rand < roulette_pos:
                return variation

    variation = None
    if user_id:
        variation = redis_db.get(USER_VARIATION.format(
                                 experiment_name, user_id))

    if not variation:
        probabilities_json = redis_db.get(PROBABILITIES.format(experiment_name))

        if probabilities_json is None:
            raise ABExperimentError(
                'Experiment {} is inactive or does not exists'
                .format(experiment_name)
            )

        probabilities = json.loads(probabilities_json)

        variation = roulette(probabilities)

        if user_id:
            redis_db.set(USER_VARIATION.format(
                         experiment_name, user_id), variation)

        redis_db.incr(RECEIVERS_COUNT.format(experiment_name, variation))

    return variation


def increment_success(experiment_name, variation_name):
    # Can put some garbage to db if names are invalid. Task for evicting them
    # from time to time might be a good idea
    import pdb;pdb.set_trace()
    redis_db.incr(SUCCESS_COUNT.format(experiment_name, variation_name))


def activate(experiment_name):
    experiment = _get_experiment(experiment_name)

    if experiment.active:
        raise ABExperimentError(
            'Experiment with name {} is already active'
            .format(experiment_name)
        )

    for variation in experiment.variations:
        redis_db.set(
            RECEIVERS_COUNT.format(experiment_name, variation.name),
            variation.receivers_count,
        )
        redis_db.set(
            SUCCESS_COUNT.format(experiment_name, variation.name),
            variation.success_count,
        )

    probabilities = {v.name: v.probability for v in experiment.variations}
    redis_db.set(PROBABILITIES.format(experiment_name),
                 json.dumps(probabilities))

    experiment.active = True
    if experiment.in_preparations:
        experiment.in_preparations = False
        experiment.started_at = datetime.now()
    experiment.save()


def deactivate(experiment_name):
    experiment = _get_experiment(experiment_name)

    if not experiment.active:
        raise ABExperimentError(
            'Experiment with name {} is already inactive'
            .format(experiment_name)
        )

    for variation in experiment.variations:
        variation.receivers_count = redis_db.get(
            RECEIVERS_COUNT.format(experiment_name, variation.name)
        )
        variation.success_count = redis_db.get(
            SUCCESS_COUNT.format(experiment_name, variation.name)
        )

    experiment.active = False
    experiment.ended_at = datetime.now()
    experiment.save()

    keys = redis_db.keys(EXPERIMENT_PATTERN.format(experiment_name) + '*')
    redis_db.delete(*keys)
