from urllib import urlencode
from urllib2 import urlopen

from django.conf import settings
from django.utils import simplejson


"""
Handy Google maps geocode search functions
"""


def find_geo(location, api_key=None):

    """
    Query Google maps for geo data on the passed in `location`.
    Returns dictionary of data if successful, otherwise None

    `location`  string  An address, whether partial or complete, to query
                        Google Maps about
    `api_key`   string  Google Maps API key. If this is left empty,
                        GOOGLE_MAPS_API_KEY setting is used instead
    """

    data = {
        'q': location,
        'output': "json",
        'oe': "utf8",
        'sensor': "false",
        'key': api_key or settings.GOOGLE_MAPS_API_KEY
    }

    url = "http://maps.google.com/maps/geo?%s" % urlencode(data)
    response = urlopen(url)
    geo_content = simplejson.loads(response.read())

    return geo_content if geo_content['Status']['code'] == 200 else None


def find_geo_point(location, api_key=None):

    """
    Use `find_geo` to query Google Maps and returns a tuple containing the
    normalized address and a point tuple containing the latitude and longitude
    points, or returns False if no data is found

    `location`  string  An address, whether partial or complete, to query
                        Google Maps about
    `api_key`   string  Google Maps API key. If this is left empty,
                        GOOGLE_MAPS_API_KEY setting is used instead
    """

    geo_content = find_geo(location, api_key)

    if geo_content:
        placemark = geo_content['Placemark'][0]
        lng, lat = placemark['Point']['coordinates'][:2]
        return (placemark['address'], (lng, lat,),)
    else:
        return geo_content
