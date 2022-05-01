from apps.tracking.rest.views import TrackingRequest
from apps.tracking.rest.viewsets import PresenceViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"presence", PresenceViewSet)
