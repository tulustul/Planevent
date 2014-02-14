import json
import datetime

from planevent import models
from planevent.redisdb import redis_cache


class PlaneventJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, models.BaseEntity):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


def create_key(key_data):
    return key_data[0].format(*key_data[1:])


def set(key_data, obj, expire=3600):
    key = create_key(key_data)

    data = json.dumps(obj, cls=PlaneventJsonEncoder)

    redis_cache.set(key, data)
    redis_cache.expire(key, expire)


def get(key_data, model=None):
    key = create_key(key_data)
    obj = redis_cache.get(key)
    if obj:
        data = json.loads(obj)
        if model:
            return model().deserialize(data)
        return data
    return None


def delete(key_data):
    key = create_key(key_data)
    redis_cache.delete(key)


def flush():
    redis_cache.flushall()
