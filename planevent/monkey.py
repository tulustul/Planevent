import inspect

from pyramid.config import util

# getargspec is deprecated, it fails on annotations
util.inspect.getargspec = inspect.getfullargspec
