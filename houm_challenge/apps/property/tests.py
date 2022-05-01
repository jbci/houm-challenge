import json
from django.test import TestCase
from .models import Property
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon

class PropertyTest(TestCase):
    """ 
    Property model exists and it has fields:
        - name: can't be null or blank, unique
        - polygon: can't be null or blank

    """
    @classmethod
    def setUpClass(self):
        super(PropertyTest, self).setUpClass()
        print("\nRunning " + str(self))

    def setUp(self):   

        geojson = json.loads(
            '{ "type": "Polygon", "coordinates": [ [ [ -70.545364012434177, -33.384806877732011 ], [ -70.544135560705513, -33.384479891442083 ], [ -70.543947806074655, -33.384784481450133 ], [ -70.545208444310617, -33.38513834203038 ], [ -70.545364012434177, -33.384806877732011 ] ] ] }')
        polygon = Polygon(geojson['coordinates'][0])

        self.valid_property_params = {
            'name': 'Home 1',
            'polygon': polygon
        }

    def test_create_valid_property(self):        
        o = Property.objects.create(**self.valid_property_params)
        o = Property.objects.get(**self.valid_property_params)
        self.assertEqual(o.name, self.valid_property_params['name'])
