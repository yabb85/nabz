from django.db import models
from vl.models import Bunny
from django.utils.translation import gettext_lazy as _
from datetime import datetime


# Create your models here.
class Frequency(models.IntegerChoices):
    VERY_OFTEN = 1200, _('very often')
    OFTEN = 3600, _('often')
    SOMETIMES = 7200, _('sometimes')
    RARELY = 10400, _('rarely')
    VERY_RARELY = 14400, _('very rarely')


class Mood(models.Model):
    bunny = models.ForeignKey(Bunny, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    frequency = models.IntegerField(choices=Frequency, default=Frequency.VERY_RARELY)
    next_date = models.DateTimeField(default=datetime.now())
