from datetime import datetime

from sqlalchemy.exc import IntegrityError

from planevent.accounts.models import Account
from planevent.core.decorators import (
    permission,
    route,
    Rest,
    Body,
)
from planevent.core.views import View
from planevent.abtesting import (
    service,
    models,
)


@route('experiments')
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

    @permission(Account.Role.ADMIN)
    def get(self, offset: int=0, limit: int=10, active: int=None):
        self.offset = offset
        self.limit = limit

        if active == 1:
            return self.get_active()
        elif active == 0:
            return self.get_inactive()
        else:
            return self.get_active() + self.get_inactive()

    @permission(Account.Role.ADMIN)
    def post(self, experiment: Body(models.Experiment)):
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


@route('activate_experiment')
class ActivateExperimentView(View):

    @permission(Account.Role.ADMIN)
    def get(self, name: Rest(str)):
        try:
            return service.activate(name)
        except service.ABExperimentError as e:
            return self.response(400, str(e))


@route('deactivate_experiment')
class DeactivateExperimentView(View):

    @permission(Account.Role.ADMIN)
    def get(self, name: Rest(str)):
        try:
            return service.deactivate(name)
        except service.ABExperimentError as e:
            return self.response(400, str(e))


@route('experiment_increment')
class ExperimentIncrementView(View):

    def get(self, name: Rest(str), variation: Rest(str)):
        try:
            service.increment_success(name, variation)
            return 'OK'
        except service.ABExperimentError as e:
            return self.response(400, str(e))


@route('experiment_variation')
class ExperimentVariationView(View):

    def get(self, name: Rest(str)):
        try:
            return service.get_variation(
                name, self.request.session.get('user_id')
            )
        except service.ABExperimentError as e:
            return self.response(400, str(e))
