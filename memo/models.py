from django.db import models
from vl.models import Bunny


# Create your models here.

class Memo(models.Model):
    bunny = models.ForeignKey(Bunny, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    messages = models.CharField(null=True, blank=True)
    last = models.IntegerField(default=0)
