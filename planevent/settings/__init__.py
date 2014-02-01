import pyramid

from planevent.settings.shared import *

with open('instance') as f:
    instance = f.read()

if instance == 'development':
    from planevent.settings.development import *
elif instance == 'production':
    from planevent.settings.production import *
else:
    raise ValueError('Unknown instance: ' + instance)


def get_config():
    return pyramid.threadlocal.get_current_registry().settings
