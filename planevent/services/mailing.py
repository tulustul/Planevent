import json

import requests
from jinja2 import Environment, FileSystemLoader

from planevent import (
    settings,
    logger,
)

env = Environment(loader=FileSystemLoader('templates/mails'))


class MailException(Exception):
    pass


def send_mail(template, to, subject, **kwargs):

    if isinstance(to, str):
        to = [to]

    template = env.get_template(template + '.pt')
    mail_body = template.render(**kwargs)

    response = requests.post(
        settings.MAILGUN_PATH,
        auth=("api", settings.MAILGUN_API_KEY),
        data={"from": settings.EMAIL_ADDRESS,
              "to": to,
              "subject": subject,
              "html": mail_body}
    )

    message = json.loads(response.content.decode('utf8'))

    if response.status_code == 200:
        logger.info('Sending email with subject "{}" to "{}"'
                    .format(subject, to))
        return message
    else:
        logger.error('Unable to send email with subject "{}" to "{}".'
                     .format(subject, to))
        raise MailException(message)
