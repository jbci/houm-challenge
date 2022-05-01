from datetime import datetime, timedelta, timezone
import time
import pymongo
import requests

def get_mongo(kwargs=dict()):
    host = 'localhost'
    port = 27017
    name = 'series_db'
    collection = 'tracking'
    mongo_client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
    nosqldb = mongo_client[name][collection]
    return nosqldb

def main():
    print("Starting mock data insertion...")
    nosqldb = get_mongo()
    nosqldb.drop()

    login_response = requests.request(
        method='POST', url='http://localhost:8000/api/token/', data={'username': 'houmer', 'password': 'houmer'})
    print(login_response.json())

    start_time = datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    unix_timestamp = datetime.timestamp(start_time)
    print(f"unix_timestamp: {unix_timestamp} start_time: {start_time}")
    for i in range(-120, 240, 60):
        current_time = start_time + timedelta(seconds=i)
        unix_timestamp = datetime.timestamp(current_time)

        if i > 120:
            insert_dict = {"timestamp": unix_timestamp, "lng": -70.5346686230096, "lat": -33.374804669077925}
        elif i >= 60:
            insert_dict = {"timestamp": unix_timestamp, "lng": -70.5446686230096, "lat": -33.38480466907792}
        else:
            insert_dict = {"timestamp": unix_timestamp, "lng": -72.545364012434177, "lat": -32.384806877732011}

        headers = {'Authorization': f'Token {login_response.json()["token"]}'}
        insert_response = requests.request(
            method='POST', url='http://localhost:8000/api/position/', data=insert_dict, headers=headers)
        x = insert_response.json()['id']
        print(f"unix_timestamp: {unix_timestamp} start_time: {current_time} x: {x}")

    results = nosqldb.count_documents({})
    print(f"Number of results: {results}")

    # results = nosqldb.find().sort('original_time')
    # for r in results:
    #     print(r)
    #     print(f"{r['original_time']} {datetime.utcfromtimestamp(r['original_time'])}")

    headers = {'Authorization': f'Token {login_response.json()["token"]}'}
    get_response = requests.request(
        method='GET', url='http://localhost:8000/api/position/', headers=headers)
    print(get_response.json())

def check_presence():
    print("checking presence...")

    login_response = requests.request(
        method='POST', url='http://localhost:8000/api/token/', data={'username': 'admin', 'password': 'admin'})
    print(login_response.json())
    headers = {'Authorization': f'Token {login_response.json()["token"]}'}

    presence_response = requests.request(
        method='GET', url='http://localhost:8000/api/presence/?user__id=2&date=2022-01-01', data={'user_id': 2, 'date': '2020-01-01'}, headers=headers)
    print(presence_response.json())

def speed_limit():
    print("speed_limit...")
    login_response = requests.request(
        method='POST', url='http://localhost:8000/api/token/', data={'username': 'admin', 'password': 'admin'})
    print(login_response.json())
    headers = {'Authorization': f'Token {login_response.json()["token"]}'}

    presence_response = requests.request(
        method='GET', url='http://localhost:8000/api/safety/speed/', data={'user_id': 2, 'date': '2022-01-01', 'threshold': 50}, headers=headers)
    print(presence_response.json())



if __name__ == '__main__':
    main()
    time.sleep(5)
    check_presence()
    speed_limit()

