from django.db import models
from vl.models import Bunny, ZStamp
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Weather(models.Model):
    class WeatherType(models.TextChoices):
        NOW = "now", _("now")
        # TOMORROW = "tomorrow", _("tomorrow")
        TODAY = "today", _("today")
    bunny = models.ForeignKey(Bunny, on_delete=models.CASCADE, null=True, blank=True)
    zstamp = models.ForeignKey(ZStamp, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(null=True, blank=True)
    action = models.CharField(null=True, blank=True)
    type = models.CharField(choices=WeatherType, default=WeatherType.NOW)
