from django.db import models
from vl.models import Bunny
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Day(models.IntegerChoices):
    MONDAY = 0, _("monday")
    TUESDAY = 1, _("tuesday")
    WEDNESDAY = 2, _("wednesday")
    THURSDAY = 3, _("thursday")
    FRIDAY = 4, _("friday")
    SATURDAY = 5, _("saturday")
    SUNDAY = 6, _("sunday")
    WEEK = 7, _("week")
    WEEKEND = 8, _("weekend")
    ALL = 9, _("all")
    __empty__ = _("(Unknown)")


class Sleep(models.Model):
    class SleepActionType(models.TextChoices):
        SLEEP = "sleep", _("sleep")
        WAKEUP = "wakeup", _("wakeup")
    bunny = models.ForeignKey(Bunny, on_delete=models.CASCADE)
    # action = models.CharField(choices=SleepActionType, default=SleepActionType.SLEEP)
    time = models.TimeField(null=True, blank=True)
    monday_wake_up = models.TimeField(null=True, blank=True)
    monday_sleep = models.TimeField(null=True, blank=True)
    tuesday_wake_up = models.TimeField(null=True, blank=True)
    tuesday_sleep = models.TimeField(null=True, blank=True)
    wednesday_wake_up = models.TimeField(null=True, blank=True)
    wednesday_sleep = models.TimeField(null=True, blank=True)
    thursday_wake_up = models.TimeField(null=True, blank=True)
    thursday_sleep = models.TimeField(null=True, blank=True)
    friday_wake_up = models.TimeField(null=True, blank=True)
    friday_sleep = models.TimeField(null=True, blank=True)
    saturday_wake_up = models.TimeField(null=True, blank=True)
    saturday_sleep = models.TimeField(null=True, blank=True)
    sunday_wake_up = models.TimeField(null=True, blank=True)
    sunday_sleep = models.TimeField(null=True, blank=True)
