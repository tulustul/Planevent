import os
from functools import wraps
import json
import random

from PIL import Image

from planevent.models import BaseEntity

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
                        param_value = type_().deserialize(json.loads(param_value))
                    else:
                        param_value = type_(param_value)
                except Exception as e:
                    raise ValueError('Cannot cast param ' + name,
                        ' to type ' + type_.__name__) from e
            return mth(self, param_value, *args, **kwargs)
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
