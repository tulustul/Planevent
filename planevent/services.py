from collections import namedtuple

from geopy import geocoders
import logging

from planevent import cache

LOCATION_KEY = 'location:{}'

LatLng = namedtuple('LatLng', ['lat', 'lng'])

def geocode_location(location_name):
    location_name = location_name.lower()
    location_geocoding = cache.get((LOCATION_KEY, location_name))
    if location_geocoding is None:
        logging.info('Geocoding location: ' + location_name)
        g = geocoders.GoogleV3()
        response = g.geocode(location_name)
        if not response:
            return None
        location_geocoding = response[1]
        cache.set((LOCATION_KEY, location_name), location_geocoding)
    return LatLng(*location_geocoding)
