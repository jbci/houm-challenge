from datetime import datetime
import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
# from django.utils import timezone
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import Distance
from apps.property.models import Property
from apps.base.utils import get_nosql_db
from apps.base.models import Setting


class Command(BaseCommand):

    help = 'Create seed data'

    def add_arguments(self, parser):
        # parser.add_argument('sample', nargs='+')
        pass

    def handle(self, *args, **options):
        self.settings_section()
        self.users_section()
        self.properties_section()
        # self.tracking_section()

    def settings_section(self):
        self.stdout.write(self.style.SUCCESS('Settings Section:'))
        max_speed_setting, created = Setting.objects.get_or_create(key='max_speed')
        max_speed_setting.value = '100'
        max_speed_setting.description = 'km/h'
        max_speed_setting.save()


    def users_section(self):
        self.stdout.write(self.style.SUCCESS('Users Section:'))
        admins = User.objects.filter(username='admin')
        if len(admins) == 0:
            print('    - Creating admin user.')
            self.admin = User.objects.create_user(
                username='admin',
                email='admin@challenge.org',
                password='admin',
                is_staff=True,
                is_active=True,
                is_superuser=True,
            )
        else:
            print('    - admin already exists.')
            self.admin = admins.first()

        users = User.objects.filter(username='houmer')
        if len(users) == 0:
            print('    - Creating houmer.')
            self.houmer = User.objects.create_user(
                username='houmer',
                email='houmer@challenge.org',
                password='houmer',
                is_staff=False,
                is_active=True,
                is_superuser=False,
            )
        else:
            print('    - houmer already exists.')
            self.houmer = users.first()

    def properties_section(self):
        self.stdout.write(self.style.SUCCESS('Properties Section:'))

        default_name = 'Casa 1'
        geojson = json.loads(
            '{ "type": "Polygon", "coordinates": [ [ [ -70.545364012434177, -33.384806877732011 ], [ -70.544135560705513, -33.384479891442083 ], [ -70.543947806074655, -33.384784481450133 ], [ -70.545208444310617, -33.38513834203038 ], [ -70.545364012434177, -33.384806877732011 ] ] ] }')
        polygon = Polygon(geojson['coordinates'][0])

        properties = Property.objects.filter(name=default_name)
        if len(properties) == 0:
            print('    - Creating Property 1.')
            self.prop_1 = Property.objects.create(
                name=default_name,
                polygon=polygon
            )
        else:
            print('    - Property 1 already exists.')
            self.prop_1 = properties.first()

        point = polygon.centroid
        for p in Property.objects.filter(polygon__contains=point):
            print(f'    - Property {p.id} contains {point}')

    def tracking_section(self):
        collection = get_nosql_db()

        insert_dict = {"user_id": self.houmer.id, "datetime": datetime.now(
        ), "location": {"long": -70.545364012434177, "lat": -33.384806877732011}}
        x = collection.insert_one(insert_dict)
        print(x.inserted_id)
        print(x)
        print(insert_dict)

        insert_dict = {"user_id": self.admin.id,  "datetime": datetime.now(
        ), "location": {"long": -70.545364012434177, "lat": -33.384806877732011}}
        x = collection.insert_one(insert_dict)
        print(x.inserted_id)
        print(x)
        print(insert_dict)

        print("listing documents")
        for x in collection.find():
            print(x)

        print("querying documents")
        mongo_query = {"user_id": self.admin.id}
        query_results = collection.find(mongo_query).sort("datetime")

        for x in query_results:
            print(x)

        print("sorting documents")
        sorted_docs = collection.find().sort("datetime")
        for x in sorted_docs:
            print(x)

        # collection.drop()
