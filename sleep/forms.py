from django.forms import ModelForm, TimeInput
from .models import Sleep


class TimeInputWidget(TimeInput):
    input_type = "time"


class SleepForm(ModelForm):
    class Meta:
        model = Sleep
        fields = [
            'monday_wake_up',
            'monday_sleep',
            'tuesday_wake_up',
            'tuesday_sleep',
            'wednesday_wake_up',
            'wednesday_sleep',
            'thursday_wake_up',
            'thursday_sleep',
            'friday_wake_up',
            'friday_sleep',
            'saturday_wake_up',
            'saturday_sleep',
            'sunday_wake_up',
            'sunday_sleep',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["monday_wake_up"].widget = TimeInputWidget()
        self.fields["monday_sleep"].widget = TimeInputWidget()
        self.fields['tuesday_wake_up'].widget = TimeInputWidget()
        self.fields['tuesday_sleep'].widget = TimeInputWidget()
        self.fields['wednesday_wake_up'].widget = TimeInputWidget()
        self.fields['wednesday_sleep'].widget = TimeInputWidget()
        self.fields['thursday_wake_up'].widget = TimeInputWidget()
        self.fields['thursday_sleep'].widget = TimeInputWidget()
        self.fields['friday_wake_up'].widget = TimeInputWidget()
        self.fields['friday_sleep'].widget = TimeInputWidget()
        self.fields['saturday_wake_up'].widget = TimeInputWidget()
        self.fields['saturday_sleep'].widget = TimeInputWidget()
        self.fields['sunday_wake_up'].widget = TimeInputWidget()
        self.fields['sunday_sleep'].widget = TimeInputWidget()
