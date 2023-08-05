import unittest
import json
from json_mapper.mapper import map_json


mapping_config = {
    'ApiResponse.ApiResponseWrapper': {
        'ResponseTimestamp': 'last_update',

        '{loop=>hotels} HotelsResponse': {
            'HotelId':  'id',
            'Country':  'country',

            '{loop=>photos} Photos': 'BigUrl',

            '{loop=>rooms} RoomsResponse': {
                'RoomId':       'id',
                'BedsCount':    'beds'
            }
        }
    }
}

mapping_config2 = {
    '{loop} ApiResponse.ApiResponseWrapper.HotelsResponse': {
        'HotelId':  'id',
        'Country':  'country',

        '{loop=>photos} Photos': 'BigUrl',

        '{loop=>rooms} RoomsResponse': {
            'RoomId':       'id',
            'BedsCount':    'beds'
        }
    }
}


class MappingTestCase(unittest.TestCase):
    def setUp(self):
        self.test_json = json.loads(open('tests/dump.json', 'r').read())

    def test_map_json(self):
        """ testing json mapping """
        result = map_json(mapping_config, self.test_json)
        self.assertTrue('last_update' in result)
        self.assertEqual('2342423423423423', result['last_update'])
        self.assertTrue('hotels' in result)

        hotels = result['hotels']
        self.assertEqual(2, len(hotels))

        hotel = hotels[0]
        self.assertTrue('id' in hotel)
        self.assertEqual('1234', hotel['id'])
        self.assertTrue('country' in hotel)
        self.assertEqual('Russia', hotel['country'])
        self.assertTrue('rooms' in hotel)
        self.assertTrue('photos' in hotel)
        self.assertEqual(2, len(hotel['photos']))

        rooms = hotel['rooms']
        self.assertEqual(2, len(rooms))

        room = rooms[0]
        self.assertTrue('id' in room)
        self.assertEqual('12312', room['id'])
        self.assertTrue('beds' in room)
        self.assertEqual('1', room['beds'])

    def test_map_json_loop(self):
        """ testin json mapping with loop first """
        result = map_json(mapping_config2, self.test_json)
        self.assertEqual(list, type(result))
        self.assertEqual(2, len(result))
