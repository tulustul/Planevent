from collections import namedtuple
import json

from geopy import geocoders
import logging

from planevent.models import redis

LOCATION_PREFIX = 'locations:'

LatLng = namedtuple('LatLng', ['lat', 'lng'])

def geocode_location(location_name):
    location_name = location_name.lower()
    location_geocoding = redis.get(LOCATION_PREFIX + location_name)
    if location_geocoding is None:
        logging.info('Geocoding location: ' + location_name)
        g = geocoders.GoogleV3()
        response = g.geocode(location_name)
        if not response:
            return None
        location_geocoding = response[1]
        redis.set(LOCATION_PREFIX + location_name,
            json.dumps(location_geocoding))
    else:
        logging.info('Location geocoding cache hit: ' + location_name)
        location_geocoding = json.loads(location_geocoding)
    return LatLng(*location_geocoding)
