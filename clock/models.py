from django.db import models
from vl.models import Bunny


# Create your models here.
class Clock(models.Model):
    bunny = models.ForeignKey(Bunny, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
