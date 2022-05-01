from django.urls import path, include

from .rest.viewsets import PropertyViewSet
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r"properties", PropertyViewSet)

urlpatterns = [
    path("", include(router.urls))
]
