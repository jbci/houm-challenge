# from django.contrib import admin
from django.contrib.gis import admin
from .models import Property

admin.site.register(Property, admin.OSMGeoAdmin)