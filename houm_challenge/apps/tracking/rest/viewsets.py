from rest_framework import viewsets
from .serializers import PresenceSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from apps.tracking.models import Presence


class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all().order_by('date')
    serializer_class = PresenceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    filterset_fields = ['id', 'date', 'user__id']

    """
    Following methods may be used by the user to alter the data in the database.
    To do so proper permissions must be defined and implemented.
    It is considered beyond the scope of this challenge.
    """
    def create(self, request):
        response = {'message': 'Create function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        response = {'message': 'Update function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None):
        response = {'message': 'Update function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        response = {'message': 'Delete function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)