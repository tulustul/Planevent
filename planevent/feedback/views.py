import math
from datetime import datetime

from planevent.feedback import models
from planevent.feedback import tasks
from planevent.accounts.models import Account
from planevent.core.decorators import (
    permission,
    route,
    Body,
    Rest,
)
from planevent.core.views import View
from planevent import settings
from planevent import services


@route('feedbacks')
class FeedbacksView(View):

    # @permission(Account.Role.ADMIN)
    def get(
        self,
        offset: int=0,
        limit: int=20,
        checked: bool=None,
    ):
        query = models.Feedback.query()
        if checked is not None:
            query = query.filter(models.Feedback.checked == checked)

        query = query.order_by(models.Feedback.created_at.desc()) \
            .limit(limit).offset(offset)

        return {
            'feedbacks': query.all(),
            'page': math.floor(offset / limit),
            'pages': math.ceil(query.count() / limit),
        }

    def put(self, feedback: Body(models.Feedback)):
        if feedback.id is not None:
            return response(
                400,
                'Can add only new feedbacks. "Id" must be empty'
            )

        feedback.checked = False
        feedback.created_at = datetime.now()
        feedback.save()

        tasks.send_new_feedback_notification(feedback)

        return feedback


@route('feedback_check')
class FeedbackCheckView(View):

    # @permission(Account.Role.ADMIN)
    def post(self, id: Rest(int)):
        feedback = models.Feedback.get(id)
        if feedback is None:
            return self.response(404, 'feedback_not_found')

        if feedback.checked:
            return self.response(409, 'feedback_already_checked')

        feedback.checked = True
        feedback.save()

        return self.response(200, 'feedback_checked')
