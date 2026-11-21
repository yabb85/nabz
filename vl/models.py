from django.db import models
from django.contrib.auth.models import User
from pytz import all_timezones

# Create your models here.
class Plugin(models.Model):
    name = models.CharField(unique=True)
    one_click = models.BooleanField()
    double_click = models.BooleanField()
    record = models.BooleanField()
    rfid = models.BooleanField()
    cron = models.BooleanField()

    @property
    def bunny(self):
        return Bunny.objects.filter(models.Q(one_click=self) | models.Q(double_click=self))


class Bunny(models.Model):
    name = models.CharField()
    sn = models.CharField()
    password = models.CharField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    connected = models.BooleanField()
    one_click = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='bunny_1', null=True)
    # one_click = models.CharField(null=True, blank=True)
    # double_click = models.CharField(null=True, blank=True)
    double_click = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='bunny_2', null=True)
    plugin_record = models.ForeignKey(Plugin, on_delete=models.CASCADE, null=True)
    plugin_active = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='bunny_3', null=True, blank=True)
    sleep_state = models.BooleanField() # TODO : create sleep status synchro avec le serveur xmpp
    lang = models.CharField(default='fr_FR')
    time_zone = models.CharField(max_length=63, choices=[(tz, tz) for tz in all_timezones])


class ZStamp(models.Model):
    serial = models.CharField(unique=True)
    name = models.CharField(null=True, blank=True)
    bunny = models.ForeignKey(Bunny, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plugin = models.CharField(null=True, blank=True)
