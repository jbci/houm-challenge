from rest_framework import serializers
from apps.tracking.models import Presence
from django.contrib.gis.geos import Point
from rest_framework_gis.serializers import GeometrySerializerMethodField


class PresenceSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) 
    property = serializers.PrimaryKeyRelatedField(read_only=True) 
    property_name = serializers.SerializerMethodField()
    property_centroid = GeometrySerializerMethodField()
    
    class Meta:
        model = Presence
        fields = [
            "id",
            "user",
            "property",
            "property_name",
            "date",
            "time_spent",
            "property_centroid"
        ]
        geo_field = 'property_centroid'

    def get_property_name(self, obj):
        return obj.property.name

    def get_property_centroid(self, obj):
        return obj.property.polygon.centroid