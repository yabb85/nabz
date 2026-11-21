from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Bunny, ZStamp, Plugin


class BunnyForm(forms.Form):
    name = forms.CharField(label=_('bunny name'))
    sn = forms.CharField(label=_('serial number'))
    # password = forms.CharField(label="mot de passe", widget=forms.PasswordInput)
    # password_2 = forms.CharField(label="confirmation du mot de passe", widget=forms.PasswordInput)


class BunnyEditForm(forms.ModelForm):
    class Meta:
        model = Bunny
        # print(plugin_choices)
        # widgets = (
            # 'one_click', forms.Select(choices=plugin_choices),
        # )
        fields = [
            'name',
            'sn',
            'one_click',
            'double_click',
            'plugin_record',
            'lang',
            'sleep_state',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['sn'].widget.attrs['readonly'] = True
            self.fields['sleep_state'].widget.attrs['disabled'] = True
        one_click_choices = [(plugin.pk, plugin.name) for plugin in Plugin.objects.filter(one_click=True).all()]
        one_click_choices.insert(0, (None, '-------'))
        self.fields['one_click'].widget = forms.Select(choices=one_click_choices)
        double_click_choices = [(plugin.pk, plugin.name) for plugin in Plugin.objects.filter(double_click=True).all()]
        double_click_choices.insert(0, (None, '-------'))
        self.fields['double_click'].widget = forms.Select(choices=double_click_choices)
        record_choices = [(plugin.pk, plugin.name) for plugin in Plugin.objects.filter(record=True).all()]
        record_choices.insert(0, (None, '-------'))
        self.fields['plugin_record'].widget = forms.Select(choices=record_choices)


class ZStampEditForm(forms.ModelForm):
    class Meta:
        model = ZStamp
        fields = [
            'name',
            'serial',
            'plugin',
        ]
