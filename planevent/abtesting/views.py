from pyramid.view import (
    view_config,
    view_defaults,
)

from planevent.decorators import param
from planevent.views import View
from planevent.redisdb import redis_db
from planevent.abtesting import (
    service as ab_service,
    models,
)


@view_defaults(route_name='experiments', renderer='json')
class ExperimentView(View):

    def get_experiments(self, active):
        query = models.Experiment.query('variations')
        if active is not None:
            query = query.filter(models.Experiment.active == active)
        return query.limit(self.limit).offset(self.offset).all()

    def get_active(self):
        # TODO redis operations in batch
        experiments = self.get_experiments(1)
        for experiment in experiments:
            for variation in experiment.variations:
                variation.receivers_count = \
                    redis_db.get(ab_service.RECEIVERS_COUNT.format(
                                 experiment.name, variation.name))
                variation.success_count = \
                    redis_db.get(ab_service.SUCCESS_COUNT.format(
                                 experiment.name, variation.name))
        return experiments

    def get_inactive(self):
        return self.get_experiments(0)

    @view_config(request_method='GET')
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    @param('active', int, default=None)
    def get(self, offset, limit, active):
        self.offset = offset
        self.limit = limit

        if active == 1:
            return self.get_active()
        elif active == 0:
            return self.get_inactive()
        else:
            return self.get_active() + self.get_inactive()

    @view_config(request_method='POST')
    @param('experiment', models.Experiment, body=True, required=True)
    def post(self, experiment):
        if experiment.id is None or experiment.in_preparations:
            experiment.save()
        else:
            self.request.response.status = 409
            return {
                'error': 'Cannot edit experiment which was previously activated'
            }


@view_defaults(route_name='activate_experiment', renderer='json')
class ActivateExperimentView(View):

    @view_config(request_method='GET')
    @param('name', str, required=True, rest=True)
    def get(self, name):
        try:
            ab_service.activate(name)
        except ab_service.ABExperimentError as e:
            self.request.response.status = 400
            return {'error': str(e)}


@view_defaults(route_name='deactivate_experiment', renderer='json')
class DeactivateExperimentView(View):

    @view_config(request_method='GET')
    @param('name', str, required=True, rest=True)
    def get(self, name):
        try:
            ab_service.deactivate(name)
        except ab_service.ABExperimentError as e:
            self.request.response.status = 400
            return {'error': str(e)}


@view_defaults(route_name='experiment_variation', renderer='json')
class ExperimentVariationView(View):

    @view_config(request_method='GET')
    @param('name', str, required=True, rest=True)
    def get(self, name):
        try:
            return ab_service.get_variation(name,
                                            self.request.session.get('user_id'))
        except ab_service.ABExperimentError as e:
            self.request.response.status = 400
            return {'error': str(e)}


@view_defaults(route_name='experiment_increment', renderer='json')
class ExperimentIncrementView(View):

    @view_config(request_method='GET')
    @param('name', str, required=True, rest=True)
    @param('variation', str, required=True, rest=True)
    def get(self, name, variation):
        try:
            ab_service.increment_success(name, variation)
        except ab_service.ABExperimentError as e:
            self.request.response.status = 400
            return {'error': str(e)}
