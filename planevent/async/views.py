from planevent.core.decorators import (
    permission,
    route,
    Rest,
)
from planevent.core.views import View
from planevent.accounts.models import Account
from planevent.async import TaskProgressCounter


@route('list_incomplete')
class ListIncompleteView(View):

    @permission(Account.Role.ADMIN)
    def get(self):
        pass


@route('task_progress')
class TaskProgressView(View):

    @permission(Account.Role.ADMIN)
    def get(self, id: Rest(int)):
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


@route('task_cancel')
class TaskCancelView(View):

    @permission(Account.Role.ADMIN)
    def post(self, id: Rest(int)):
        try:
            TaskProgressCounter.cancel(id)
        except ValueError as e:
            self.request.response.status = 404
            return {'error': str(e)}
        else:
            return 'Task {} canceled'.format(id)
