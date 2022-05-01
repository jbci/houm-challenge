from rest_framework import viewsets
from .serializers import PropertySerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from apps.property.models import Property

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
