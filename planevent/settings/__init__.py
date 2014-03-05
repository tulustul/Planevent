import sys

import pyramid

from planevent.settings.shared import *

testing = sys.argv[0].endswith('nosetests')

if testing:
    from planevent.settings.testing import *
else:
    with open('instance') as f:
        instance = f.read().strip()

    if instance == 'development':
        from planevent.settings.development import *
    elif instance == 'production':
        from planevent.settings.production import *
    elif instance == 'staging':
        from planevent.settings.staging import *
    else:
        raise ValueError('Unknown instance: ' + instance)


def get_config():
    return pyramid.threadlocal.get_current_registry().settings
