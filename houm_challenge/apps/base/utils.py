import pymongo
from django.conf import settings
from datetime import datetime
    
def get_mongo(kwargs=dict()):
    """
    Returns a pymongo database object.
    """
    host = settings.DATABASES['timeseries']['HOST']
    port = settings.DATABASES['timeseries']['PORT']
    name = kwargs.get('name',settings.DATABASES['timeseries']['NAME'])
    collection = kwargs.get('collection',settings.DATABASES['timeseries']['COLLECTION'])
    mongo_client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
    nosqldb = mongo_client[name][collection]
    return nosqldb

def get_nosql_db(kwargs=dict()):
    """
    Returns a noslqdb database object.
    """
    database_types = {
        "mongo": get_mongo,
    }
    return database_types[settings.DATABASES['timeseries']['TYPE']](kwargs)

def is_valid_str(param_value):
    return True

def is_valid_float(param_value):
    return True

def is_valid_timestamp(param_value):
    return True

def is_valid_lat(param_value):
    return -90 <= param_value <= 90

def is_valid_lng(param_value):
    return -180 <= param_value <= 180

def is_valid_param(param_value, param_type, allowed_empty=False):
    """
    Validation router.
    """
    if not allowed_empty and param_value is None:
        return False

    param_types = {
        str: is_valid_str,
        float: is_valid_float,
        'timestamp': is_valid_timestamp,
        'lat': is_valid_lat,
        'lng': is_valid_lng,
    }
    return param_types[param_type](param_value)
