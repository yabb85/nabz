from django.forms import ModelForm
from .models import Clock


class ClockForm(ModelForm):
    class Meta:
        model = Clock
        fields = [
            'bunny',
            'enabled',
        ]

    # def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        # self
