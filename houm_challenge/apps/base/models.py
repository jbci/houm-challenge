from django.db import models

class Setting(models.Model):
    
    description = models.CharField(
        max_length=64, 
        unique=True,
    )

    key = models.CharField(
        max_length=32, 
        unique=True,
    )

    value = models.CharField(
        max_length=256, 
    )
    
    @classmethod
    def get(cls, key=key):
        return Setting.objects.get(key=key).value