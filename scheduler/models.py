from django.db import models

# Create your models here.
class Schedule(models.Model):
    datetime = models.DateTimeField()
    url = models.CharField()
    service = models.CharField()
