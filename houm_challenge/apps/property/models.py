from django.db import models
from django.contrib.gis.db.models import PolygonField
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext as _

class Property(models.Model):

    name  = models.CharField(
        max_length=128,
        blank=False,        
        unique=True,
        null=False, 
        validators = [MinLengthValidator(limit_value=3, message=_("The length must be over 3"))],
        verbose_name=_('Name'))

    polygon = PolygonField(
        null=False, 
        blank=False)

    def __str__(self):
        return f"Property-{self.id}-{self.name}"

    class Meta:
        app_label = "property"
        verbose_name =  _("Property")
        verbose_name_plural = _("Properties")
        ordering = ("id",)