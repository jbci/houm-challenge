import pymongo
from celery import shared_task
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from apps.base.utils import get_nosql_db
from apps.property.models import Property
from .models import Presence


@shared_task
def property_presence():
    """Processing of pending position data.

    This task is intended to be run periodically by a celery beat.
    """
    nosql_db = get_nosql_db()
    for user in User.objects.all():
        # prepare dictionary for query
        mongo_query = {
            "user_id": user.id,
            "status": "pending"
        }
        # perform query to nosql db
        query_results = nosql_db.find(mongo_query) \
            .sort("original_time", pymongo.DESCENDING)
        # ensure variable previous_result is initialized
        previous_result = None
        # iterate over results in pairs to calculate time elapsed
        for index, result in enumerate(query_results):
            # find if current result is inside any property
            current_point_properties = contained_by_properties(result)
            # ensure variable prev_point_properties is initialized
            prev_point_properties = []
            # if previous_result is not None, find if is inside any property
            if previous_result:
                prev_point_properties = contained_by_properties(previous_result)
            # calculate the intersection of the two sets
            intersection = list(set(current_point_properties)
                                .intersection(set(prev_point_properties)))
            # iterate over intersecting properties ids
            for property_id in intersection:
                # prepare the missing defining elements of the presence object
                property = Property.objects.get(id=property_id)
                day = datetime.fromtimestamp(int(float(result['original_time']))).date()
                # recover uniquely identified if presence object already exists
                presence = Presence.objects.filter(user=user, property=property, date=day).first()
                # create with time_spent = 0, uniquely identified if presence object not exists
                if not presence:
                    presence = Presence.objects.create(
                        user=user,
                        property=property,
                        date=day,
                        time_spent=0)
                # calculate elapsed time between current and previous position and increase time_spent
                presence.time_spent = (float(previous_result['original_time'])
                                       - float(result['original_time'])) \
                                      + presence.time_spent
                # save presence object
                presence.save()
            # update result record in nosql_db with status = processed, in order to avoid reprocessing
            updated = nosql_db.update_one({"_id": result["_id"]}, {"$set": {"status": "processed"}})
            # current result becomes previous result for next iteration
            previous_result = result


def contained_by_properties(result):
    """Find all properties that contain the given point."""
    lat = result['location']["lat"]
    lng = result['location']["lng"]
    point = Point((lng, lat))
    return [p.id for p in Property.objects.filter(polygon__contains=point)]
