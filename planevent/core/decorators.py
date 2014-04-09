import os
from functools import wraps
import json
import random
import time
import logging

from PIL import Image

# from pyramid.view import (
#     view_config,
#     view_defaults,
# )
from pyramid.exceptions import Forbidden

from planevent.core.sql import BaseEntity
# import planevent


# def view(route_name, renderer='json', **kwargs):
#     def wrap_http_verb(cls, verb):
#         if hasattr(cls, verb):
#             fun = getattr(cls, verb)
#             # view_config_decorator = view_config(request_method=verb.upper())
#             # setattr(cls, verb, view_config_decorator(fun))

#             # view_config_decorator = view_config(route_name='home', request_method='GET', renderer='../templates/index.jinja2')
#             # cls.get = view_config_decorator(cls.get)

#     def decorator(cls):
#         import pdb;pdb.set_trace()
#         view_defaults_decorator = view_defaults(
#             route_name=route_name,
#             renderer=renderer,
#             **kwargs
#         )

#         decorated_class = view_defaults_decorator(cls)

#         for http_verb in ['get', 'post', 'put', 'delete']:
#             wrap_http_verb(decorated_class, http_verb)

#         return decorated_class

#     return decorator


# class view(object):
#     HTTP_VERBS = ['get', 'post', 'put', 'delete']

#     def __init__(self, route_name, renderer='json', **kwargs):
#         self.settings = dict(
#             route_name=route_name,
#             renderer=renderer,
#             **kwargs
#         )

#     def register_http_verb(self, cls, verb):
#         if hasattr(cls, verb):
#             fun = getattr(cls, verb)

#             planevent.config.add_view(
#                 fun,
#                 request_method=verb.upper(),
#                 **self.settings
#             )

#     def __call__(self, cls):
#         for http_verb in self.HTTP_VERBS:
#             self.register_http_verb(cls, http_verb)
#         return cls


def permission(permission):
    '''Can decorate only View verb '''
    def decorator(mth):
        @wraps(mth)
        def wrap(self, *args, **kwargs):
            # if self.get_user_role() < permission:
            #     raise Forbidden()
            return mth(self, *args, **kwargs)
        return wrap
    return decorator


def param(name, type_, body=False, rest=False, required=False, default=None):
    def decorator(mth):
        @wraps(mth)
        def wrap(self, *args, **kwargs):
            if body:
                param_value = self.request.body.decode("utf-8")
            else:
                params = self.request.matchdict if rest else self.request.params
                param_value = params.get(name)
            if param_value is None:
                if required:
                    raise ValueError('Missing request param: ' + name)
                param_value = default
            else:
                try:
                    if issubclass(type_, BaseEntity):
                        param_value = type_().deserialize(
                            json.loads(param_value)
                        )
                    else:
                        param_value = type_(param_value)
                except Exception as e:
                    raise TypeError(
                        'Cannot cast param {} to type {}. {}. \nParam: {}'
                        .format(name, type_.__name__, e, param_value)
                    )
            kwargs[name] = param_value
            return mth(self, *args, **kwargs)
        return wrap
    return decorator


class image_upload(object):
    def __init__(self, repo_path, size=None):
        self.repo_path = repo_path
        self.size = size

    def prepare_unique_filename(self, filename):
        while os.path.exists(self.repo_path + filename):
            filename = str(random.randrange(0, 10)) + filename
        return filename

    def prepare_image(self, input_file, output_file_path):
        image = Image.open(input_file)
        if self.size:
            image.thumbnail(self.size, Image.ANTIALIAS)
        image.save(output_file_path, 'PNG')

    def __call__(self, mth):
        @wraps(mth)
        def wrap(instance, *args, **kwargs):
            file_upload = instance.request.POST['file']

            output_file_path = self.repo_path + \
                self.prepare_unique_filename(file_upload.filename)
            input_file = file_upload.file
            self.prepare_image(input_file, output_file_path)

            return mth(instance, output_file_path, *args, **kwargs)
        return wrap


def time_profiler(profile_name):
    def decorator(mth):
        @wraps(mth)
        def wrap(*args):
            startTime = time.time()
            result = mth(*args)
            endTime = time.time()
            timeCount = endTime - startTime
            logging.info(profile_name + ' ' + mth.__name__ + ' time: \t'
                         + '%.2f' % (timeCount*1000) + ' ms')
            return result
        return wrap
    return decorator
