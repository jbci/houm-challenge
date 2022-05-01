import json
import time
from unicodedata import name
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token

from apps.base.utils import get_nosql_db
from .rest.views import TrackingRequest


class TrackingTest(TestCase):
    """
    Test Class for TrackingRequest
    """
    @classmethod
    def setUpClass(self):
        super(TrackingTest, self).setUpClass()
        print("\nRunning " + str(self))

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = TrackingRequest.as_view()
        self.user = User.objects.create_user(
            username='test_user', email='user@challenge.cl', password='password')
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.nosql_db = get_nosql_db()
        self.nosql_db.drop()

    def test_post_by_authenticated_user_returns_200(self):
        request_dict = {
            'timestamp': time.time(),
            'lat': -70.1,
            'lng': -33.1,
        }
        request = self.factory.post('/api/position/', request_dict)
        force_authenticate(request, token=self.token.key)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_by_unauthenticated_user_returns_401(self):
        request_dict = {
            'timestamp': time.time(),
            'lat': -70.545364012434177,
            'lng': -33.384806877732011,
        }
        request = self.factory.post('/api/position/', request_dict)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_return_bad_request_if_missing_lat(self):
        request_dict = {
            'timestamp': time.time(),
            'lng': -33.384806877732011,
        }
        request = self.factory.post('/api/position/', request_dict)
        force_authenticate(request, token=self.token.key)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_bad_request_if_wrong_lng(self):
        request_dict = {
            'timestamp': time.time(),
            'lat': -33.384806877732011,
            'lng':  360,
        }
        request = self.factory.post('/api/position/', request_dict)
        force_authenticate(request, token=self.token.key)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_bad_request_if_missing_timestamp(self):
        request_dict = {
            'lng': -33.384806877732011,
            'lat': -33.384806877732011,
        }
        request = self.factory.post('/api/position/', request_dict)
        force_authenticate(request, token=self.token.key)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nosqldb_insert_from_endpoint(self):
        request_dict = {
            'timestamp': time.time(),
            'lat': -70.2,
            'lng': -33.2,
        }
        request = self.factory.post('/api/position/', request_dict)
        force_authenticate(request, token=self.token.key)
        response = self.view(request)
        results = self.nosql_db.find_one()

        self.assertEqual(results['location']['lat'], request_dict['lat'])

    def test_user_auth(self):
        request_dict = {
            'timestamp': time.time(),
            'lat': -70.2,
            'lng': -33.2,
        }
        request = self.factory.post('/api/position/', request_dict)
        force_authenticate(request, user=self.user)
        response = self.view(request)
        results = self.nosql_db.find_one()

        self.assertEqual(results['location']['lat'], request_dict['lat'])
