from django.forms import ModelForm, Select
from .models import Weather
from vl.models import Bunny, ZStamp


class WeatherForm(ModelForm):
    class Meta:
        model = Weather
        fields = [
            'bunny',
            'zstamp',
            'action',
            'city',
            'type',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        if user:
            del kwargs['user']
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            if instance.bunny:
                user = instance.bunny.user
            elif instance.zstamp:
                user = instance.zstamp.user
        bunny_choices = [(plugin.pk, plugin.name) for plugin in Bunny.objects.filter(user=user).all()]
        bunny_choices.insert(0, (None, '-------'))
        self.fields['bunny'].widget = Select(choices=bunny_choices)
        zstamp_choices = [(plugin.pk, plugin.name) for plugin in ZStamp.objects.all()]
        zstamp_choices.insert(0, (None, '-------'))
        self.fields['zstamp'].widget = Select(choices=zstamp_choices)
