from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from apps.property.models import Property


class Presence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    date = models.DateField()
    time_spent = models.IntegerField()

    class Meta:
        app_label = "tracking"
        verbose_name = _("Presence")
        verbose_name_plural = _("Presences")
        ordering = ("id",)
