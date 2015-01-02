from planevent import (
    services,
    settings,
)
from planevent.async import async


@async
def send_new_feedback_notification(feedback):
    admin_mails = [admin.email for admin in settings.ADMINS]
    if admin_mails:
        services.send_mail(
            template='new_feedback_notification',
            recipients=admin_mails,
            subject='Nowy feedback',
            feedback=feedback,
        )
