from rest_framework import serializers
from apps.property.models import Property


class PropertySerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Property
        fields = [
            "id",
            "name",
            "polygon",
        ]