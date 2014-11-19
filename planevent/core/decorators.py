import os
from functools import wraps
import json
import random
import time
import logging

from PIL import (
    Image,
    ImageOps,
)
from pyramid.httpexceptions import HTTPFound
from pyramid.exceptions import Forbidden

from planevent.patches import robot_detection
from planevent.core.sql import BaseEntity
from planevent import settings
import planevent


class Param(object):
    def __init__(self, type_):
        self.type_ = type_


class Rest(Param):
    pass


class Body(Param):
    pass


class Query(Param):
    pass


class Template(object):
    def __init__(self, template_path):
        self.template_path = template_path


class Json(object):
    pass


class route(object):
    HTTP_VERBS = ['get', 'post', 'put', 'delete']

    def __init__(self, route_name, **kwargs):
        self.route_name = route_name
        self.kwargs = kwargs

    def __call__(self, cls):
        for verb in self.HTTP_VERBS:
            if hasattr(cls, verb):
                self.process_method(cls, verb)
        return cls

    def process_method(self, cls, verb):
        self.process_annotations(cls, verb)
        self.wrap_http_verb(cls, verb)

    def get_renderer(self):
        if isinstance(self.response_config, Json):
            return 'json'
        elif isinstance(self.response_config, Template):
            template_path = self.response_config.template_path
            return '../templates/{}.jinja2'.format(template_path)

    def wrap_http_verb(self, cls, verb):
        if hasattr(cls, verb):
            mth = getattr(cls, verb)
            planevent.config.add_view(
                cls, attr=mth.__name__,
                route_name=self.route_name,
                request_method=verb.upper(),
                renderer=self.get_renderer(),
                **self.kwargs
            )

    def process_annotations(self, cls, verb):
        mth = getattr(cls, verb)

        annotions = mth.__annotations__

        if 'return' in annotions:
            self.response_config = annotions.pop('return')
        else:
            self.response_config = Json()

        for arg_name, param in annotions.items():
            if not isinstance(param, Param):
                param = Query(param)
            decorator = param_decorator(arg_name, param)
            mth = decorator(mth)

        setattr(cls, verb, mth)


class seo_route(route):
    def process_method(self, cls, verb):
        super().process_method(cls, verb)
        mth = getattr(cls, verb)
        mth = seo_view_decorator(mth)
        setattr(cls, verb, mth)


def seo_view_decorator(mth):
    @wraps(mth)
    def wrap(self, *args, **kwargs):
        if not robot_detection.is_robot(self.request.user_agent):
            return HTTPFound(
                location='/#{}?{}'
                .format(self.request.path, self.request.query_string)
            )
        return mth(self, *args, **kwargs)
    return wrap


def param_decorator(name, param):
    def decorator(mth):
        @wraps(mth)
        def wrap(self, *args, **kwargs):
            param_type = param.type_
            param_class = param.__class__

            if param_class == Body:
                param_value = self.request.body.decode("utf-8")
            elif param_class == Rest:
                param_value = self.request.matchdict.get(name)
            elif param_class == Query:
                param_value = self.request.params.get(name)
            else:
                raise TypeError(
                    'Unknown param class: {}'
                    .format(param_class.__name__)
                )

            if param_value is not None:
                try:
                    if issubclass(param_type, BaseEntity):
                        param_value = param_type().deserialize(
                            json.loads(param_value)
                        )
                    elif param_type is bool:
                        param_value = bool(int(param_value))
                    else:
                        param_value = param_type(param_value)
                except Exception as e:
                    raise TypeError(
                        'Cannot cast param {} to type {}. {}. \nParam: {}'
                        .format(name, param_type.__name__, e, param_value)
                    ) from e
                kwargs[name] = param_value

            return mth(self, *args, **kwargs)
        return wrap
    return decorator


def permission(permission):
    '''Can decorate only View verb '''
    def decorator(mth):
        @wraps(mth)
        def wrap(self, *args, **kwargs):
            if settings.USE_PERMISSIONS and self.get_user_role() < permission:
                raise Forbidden()
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
            image = ImageOps.fit(image, self.size, Image.ANTIALIAS)
        image.save(output_file_path, 'PNG')

    def __call__(self, mth):
        @wraps(mth)
        def wrap(instance, *args, **kwargs):
            file_upload = instance.request.POST['file']

            if hasattr(instance, 'filename'):
                filename = instance.filename + '.png'
            else:
                filename = self.prepare_unique_filename(file_upload.filename)

            output_file_path = self.repo_path + filename
            input_file = file_upload.file
            self.prepare_image(input_file, output_file_path)

            output_file_path = '/' + output_file_path

            return mth(instance, output_file_path, *args, **kwargs)
        return wrap


def time_profiler(profile_name):
    def decorator(mth):
        @wraps(mth)
        def wrap(*args, **kwargs):
            startTime = time.time()
            result = mth(*args, **kwargs)
            endTime = time.time()
            timeCount = endTime - startTime
            logging.info(profile_name + ' ' + mth.__name__ + ' time: \t'
                         + '%.2f' % (timeCount * 1000) + ' ms')
            return result
        return wrap
    return decorator
