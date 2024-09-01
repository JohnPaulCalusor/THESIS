from django import forms
from .models import Attendance
from .models import EventRegistration
from .models import Event

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('user', 'event', 'attended')

class EventRegistrationForm(forms.ModelForm):
    receipt_file = forms.FileField(required=True)

    class Meta:
        model = EventRegistration
        fields = ('event',)

    def __init__(self, user, event, *args, **kwargs):
        super(EventRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['start_date_of_event'] = forms.DateField(initial=event.startDate, disabled=True)
        self.fields['end_date_of_event'] = forms.DateField(initial=event.endDate, disabled=True)

        # Add additional fields
        self.fields['membership_id'] = forms.CharField(initial=user.id, disabled=True)
        self.fields['name'] = forms.CharField(initial=event.eventName, disabled=True)
        self.fields['amount'] = forms.DecimalField(initial=event.price, disabled=True)
        self.fields['venue'] = forms.CharField(initial=event.venue, disabled=True)
    def save(self, commit=True):
        event_registration = super(EventRegistrationForm, self).save(commit=False)
        event_registration.user = self.user
        event_registration.receipt = self.cleaned_data['receipt_file'].read()
        if commit:
            event_registration.save()
        return event_registration