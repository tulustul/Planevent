import redis
import json
import datetime

from planevent import models

redis_db = None


class PlaneventJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, models.BaseEntity):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


def createRedisConnection(settings):
    global redis_db
    redis_db = redis.StrictRedis(
        host=settings['redis.url'],
        port=int(settings['redis.port']),
        db=settings['redis.db'],
        charset='utf-8', decode_responses=True
    )


def create_key(key_data):
    return key_data[0].format(*key_data[1:])


def set(key_data, obj, expire=3600):
    key = create_key(key_data)

    data = json.dumps(obj, cls=PlaneventJsonEncoder)

    redis_db.set(key, data)
    redis_db.expire(key, expire)


def get(key_data, model=None):
    key = create_key(key_data)
    obj = redis_db.get(key)
    if obj:
        data = json.loads(obj)
        if model:
            return model().deserialize(data)
        return data
    return None


def delete(key_data):
    key = create_key(key_data)
    redis_db.delete(key)


def flush():
    redis_db.flushall()
