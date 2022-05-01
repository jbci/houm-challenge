from datetime import datetime, timedelta
import pymongo
import time
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from apps.base.utils import get_nosql_db, is_valid_param
from apps.tracking.tasks import property_presence
from geopy.distance import distance as geopy_distance
from apps.base.utils import get_nosql_db
from apps.base.models import Setting


class TrackingRequest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """TrackingRequest GET method.
        
        Requests to this endpoint will trigger the property_presence task.
        """
        property_presence.delay()

        response = {}
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """TrackingRequest POST method.
        
        Requests to this endpoint will insert an object  to the nosql database.
        """
        try:
            # User recovery from token
            token = request.auth
            if token:
                user = Token.objects.get(key=token).user
            else:
                user = request.user
            if not user or not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            # Params recovery and validation section
            timestamp = request.data.get('timestamp')
            lat = float(request.data.get('lat', 1000))
            lng = float(request.data.get('lng', 1000))
            if not is_valid_param(timestamp, 'timestamp'):
                response = {'message': 'Wrong timestamp parameter.'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if not is_valid_param(lat, 'lat'):
                response = {'message': 'Wrong lat parameter.'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if not is_valid_param(lng, 'lng'):
                response = {'message': 'Wrong lng parameter.'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            # prepare and insert dictionary to nosql db
            insert_dict = {"user_id": user.id,
                           "original_time": float(timestamp),
                           "insert_time": time.time(),
                           "location": {"lng": lng,
                                        "lat": lat},
                           "status": "pending"}
            nosqldb = get_nosql_db()
            doc = nosqldb.insert_one(insert_dict)

            # response preparation and return
            response = {"id": str(doc.inserted_id.__str__())}
            return Response(response, status=status.HTTP_200_OK)
        
        # Exception handling
        except Exception as e:
            print(e)
            response = {
                'message': 'An error occurred while processing request.'}
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SpeedLimitRequest(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request, format=None):
        try:
            # params recovery and preparation for query
            user_id = request.data.get('user_id')
            day = request.data.get('date', '2022-04-21')
            max_speed_setting = float(request.data.get('threshold', Setting.get(key='max_speed')))
            user = User.objects.get(id=user_id)
            day_start = datetime.strptime(day, "%Y-%m-%d")
            day_end = day_start + timedelta(days=1)
            timestamp_start = datetime.timestamp(day_start)
            timestamp_end = datetime.timestamp(day_end)

            # query preparation and execution
            nosql_db = get_nosql_db()
            mongo_query = {"user_id": user.id, "original_time": {"$gte": timestamp_start, "$lt": timestamp_end}}
            query_results = nosql_db.find(mongo_query).sort("original_time", pymongo.DESCENDING)

            # prepare variables needed in the loop
            prev_result = None
            returned_results = []
            result_count = 0

            #iterate over query results in pairs
            for index, result in enumerate(query_results):
                current_point = Point((result['location']["lng"], result['location']["lat"]))

                # if the current result is not the first one, we can process the pair
                if prev_result:
                    prev_point = Point((prev_result['location']["lng"], prev_result['location']["lat"]))

                    # calculate speed in km/h based on distance and time
                    elapsed_time_in_seconds = (float(prev_result['original_time']) - float(result['original_time']))
                    elapsed_time_in_hours = elapsed_time_in_seconds / 3600
                    distance_in_kilometers = geopy_distance(current_point, prev_point).km
                    speed_in_km_per_hour = distance_in_kilometers / elapsed_time_in_hours

                    # prepare and return element if max speed is exceeded
                    if speed_in_km_per_hour > max_speed_setting:
                        result_count += 1
                        dict_to_return = dict()
                        dict_to_return["user_id"] = result['user_id']   
                        dict_to_return["start_utc_time"] = datetime.utcfromtimestamp(result['original_time'])
                        dict_to_return["end_utc_time"] = datetime.utcfromtimestamp(prev_result['original_time'])
                        dict_to_return["speed_in_km_per_hour"] = speed_in_km_per_hour
                        returned_results.append(dict_to_return)

                # current result becomes previous result for next iteration
                prev_result = result

            # prepare and return response dictionary
            response = {"results": returned_results, "count": result_count}
            return Response(response, status=status.HTTP_200_OK)

        # Exception handling
        except Exception as e:
            print(e)
            response = {
                'message': 'An error occurred while processing request.'}
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)