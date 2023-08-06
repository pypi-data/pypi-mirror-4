from django.utils import unittest

from geetar import google_maps


class GoogleMapsTestCase(unittest.TestCase):

    def test_find_geo(self):
        
        # Valid locations
        
        locations = [
            '7719 N. McKenna Ave., Portland, OR',
            'Los Angeles, CA',
            '90210'
        ]
        
        for location in locations:
            self.assertIsInstance(google_maps.find_geo(location), dict, "Valid address doesn't return a dict object: %s" % location)
        
        # Invalid locations

        empty = google_maps.find_geo('')
        self.assertEqual(empty, None, "Blank location doesn't return None: %s" % str(empty))

    def test_find_geo_point(self):

        # Valid locations

        locations = [
            '419 NE 10th Ave., Portland, OR 97232',
            'Mexico',
            'New York, NY',
            'Illinois'
        ]

        for location in locations:
            result = google_maps.find_geo_point(location)
            self.assertIsInstance(result, tuple, "Valid address doesn't return a tuple: %s, returns: %s" % (location, str(result)))
            self.assertIsInstance(result[0], (str, unicode,), "First tuple element is not a string for location: %s, returns: %s" % (location, type(result[0])))
            self.assertIsInstance(result[1][0], float, "2nd tuple element doesn't have a float for first item: %s, returns: %s" % (location, type(result[1][0])))
            self.assertIsInstance(result[1][1], float, "First tuple element is not a string for location: %s, returns: %s" % (location, type(result[0])))

        # Invalid locations

        invalid_locations = [
            '',
            'sfhrgurhkj'
        ]

        for location in invalid_locations:
            result = google_maps.find_geo_point(location)
            self.assertEqual(result, None)
