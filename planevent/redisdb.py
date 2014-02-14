import redis
from planevent import settings

redis_cache = None
redis_db = None


def createConnection(db_no):
    return redis.StrictRedis(
        host=settings.REDIS['URL'],
        port=int(settings.REDIS['PORT']),
        password=settings.REDIS['PASSWORD'],
        db=db_no,
        charset='utf-8', decode_responses=True
    )


def createConnections():
    global redis_cache, redis_db
    redis_cache = createConnection(settings.REDIS['CACHE_DB'])
    redis_db = createConnection(settings.REDIS['DB'])
