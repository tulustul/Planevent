import json
import re

import requests
from jinja2 import Environment, FileSystemLoader

from planevent import (
    settings,
    logger,
)

env = Environment(loader=FileSystemLoader('templates/mails'))

MAIL_REGEX = '^.+@.+\..{2,3}$'


class MailException(Exception):
    pass


class InvalidEmail(MailException):
    pass


def validate_to(to):
    for email in to:
        if not re.match(MAIL_REGEX, email):
            raise InvalidEmail()


def send_mail(template, to, subject, **kwargs):

    if isinstance(to, str):
        to = [to]

    validate_to(to)

    template = env.get_template(template + '.jinja2')
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
