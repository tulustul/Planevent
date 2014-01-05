from functools import wraps
import json

from planevent.models import BaseEntity

def param(name, type_, rest=False, required=False):
    def decorator(mth):
        @wraps(mth)
        def wrap(self, *args, **kwargs):
            params = self.request.matchdict if rest else self.request.params
            param_value = params.get(name)
            if required and param_value is None:
                raise ValueError('Missing request param: ' + name)
            if param_value:
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
