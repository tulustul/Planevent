from datetime import datetime

from sqlalchemy.exc import IntegrityError

from pyramid.view import (
    view_config,
    view_defaults,
)

from planevent.accounts.models import Account
from planevent.core.decorators import (
    param,
    permission,
)
from planevent.core.views import View
from planevent.abtesting import (
    service,
    models,
)


@view_defaults(route_name='experiments', renderer='json')
class ExperimentView(View):

    def get_experiments(self, active):
        query = models.Experiment.query('variations') \
            .order_by(models.Experiment.created_at.desc())

        if active is not None:
            query = query.filter(models.Experiment.active == active)

        return query.limit(self.limit).offset(self.offset).all()

    def get_active(self):
        # TODO redis operations in batch
        experiments = self.get_experiments(1)
        for experiment in experiments:
            for variation in experiment.variations:
                variation.receivers_count = service.get_receivers_count(
                    experiment.name, variation.name)

                variation.success_count = service.get_success_count(
                    experiment.name, variation.name)

        return experiments

    def get_inactive(self):
        return self.get_experiments(0)

    @view_config(request_method='GET')
    @permission(Account.Role.ADMIN)
    @param('offset', int, default=0)
    @param('limit', int, default=10)
    @param('active', int, required=None, default=None)
    def get(self, offset, limit, active):
        self.offset = offset
        self.limit = limit

        if active == 1:
            return self.get_active()
        elif active == 0:
            return self.get_inactive()
        else:
            return self.get_active() + self.get_inactive()

    @view_config(request_method='POST', renderer='json')
    @permission(Account.Role.ADMIN)
    @param('experiment', models.Experiment, body=True, required=True)
    def post(self, experiment):
        unique_names_count = len({v.name for v in experiment.variations})
        if unique_names_count < len(experiment.variations):
            return self.response(409, 'Variations must have unique names')

        if experiment.id is None:
            experiment.created_at = datetime.now()
            experiment.in_preparations = True
            experiment.active = False
        else:
            original_experiment = models.Experiment.get(experiment.id)

            experiment.in_preparations = original_experiment.in_preparations
            experiment.active = original_experiment.active
            experiment.winner_name = original_experiment.winner_name
            experiment.created_at = original_experiment.created_at
            experiment.started_at = original_experiment.started_at
            experiment.ended_at = original_experiment.ended_at

        if not experiment.in_preparations:
            return self.response(
                409,
                'Cannot edit experiment which was previously activated'
            )

        try:
            experiment.save()
        except IntegrityError as e:
            return self.response(409, 'Data integrity error: ' + str(e))
        return experiment


@view_defaults(route_name='activate_experiment', renderer='json')
class ActivateExperimentView(View):

    @view_config(request_method='GET')
    @permission(Account.Role.ADMIN)
    @param('name', str, required=True, rest=True)
    def get(self, name):
        try:
            return service.activate(name)
        except service.ABExperimentError as e:
            return self.response(400, str(e))


@view_defaults(route_name='deactivate_experiment', renderer='json')
class DeactivateExperimentView(View):

    @view_config(request_method='GET')
    @permission(Account.Role.ADMIN)
    @param('name', str, required=True, rest=True)
    def get(self, name):
        try:
            return service.deactivate(name)
        except service.ABExperimentError as e:
            return self.response(400, str(e))


@view_defaults(route_name='experiment_increment', renderer='json')
class ExperimentIncrementView(View):

    @view_config(request_method='GET')
    @param('name', str, required=True, rest=True)
    @param('variation', str, required=True, rest=True)
    def get(self, name, variation):
        try:
            service.increment_success(name, variation)
            return 'OK'
        except service.ABExperimentError as e:
            return self.response(400, str(e))


@view_defaults(route_name='experiment_variation', renderer='json')
class ExperimentVariationView(View):

    @view_config(request_method='GET')
    @param('name', str, required=True, rest=True)
    def get(self, name):
        try:
            return service.get_variation(
                name, self.request.session.get('user_id')
            )
        except service.ABExperimentError as e:
            return self.response(400, str(e))
