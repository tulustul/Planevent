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
from planevent.async import TaskProgressCounter


@view_defaults(route_name='list_incomplete', renderer='json')
class ListIncompleteView(View):

    @view_config(request_method='GET')
    @permission(Account.Role.ADMIN)
    def get(self):
        pass


@view_defaults(route_name='task_progress', renderer='json')
class TaskProgressView(View):

    @view_config(request_method='GET')
    @permission(Account.Role.ADMIN)
    @param('id', int, rest=True)
    def get(self, id):
        try:
            progress = TaskProgressCounter.get(id)
        except ValueError as e:
            self.request.response.status = 404
            return {'error': str(e)}
        else:
            return {
                'id': progress.id,
                'progress': progress.progress,
                'max': progress.max,
                'status': progress.status,
                'message': progress.message,
            }


@view_defaults(route_name='task_cancel', renderer='json')
class TaskCancelView(View):

    @view_config(request_method='POST')
    @permission(Account.Role.ADMIN)
    @param('id', int, rest=True)
    def post(self, id):
        try:
            TaskProgressCounter.cancel(id)
        except ValueError as e:
            self.request.response.status = 404
            return {'error': str(e)}
        else:
            return 'Task {} canceled'.format(id)
