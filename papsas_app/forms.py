from django import forms
from .models import Attendance, EventRegistration, Event, User, UserMembership, MembershipTypes
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, EmailInput

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name','mobileNum', 'region', 'address', 'occupation', 'age', 'birthdate')
        widgets = {
            'email' : forms.EmailInput(attrs={
                'placeholder' : 'Email',
                'class': 'input-field'
            }),
            'password' : forms.PasswordInput(render_value=True, attrs={
                'placeholder' : 'Password',
                'class': 'input-field'
            }),
            'birthdate' : forms.DateInput(attrs={
                'type': 'date',
                'placeholder' : 'Birth Date',
                'class': 'input-field'
            }),
            'first_name' : forms.TextInput(attrs={
                'placeholder' : 'First Name',
                'class': 'input-field'
            }),
            'last_name' : forms.TextInput(attrs={
                'placeholder' : 'Last Name',
                'class': 'input-field'
            }),
            'mobileNum' : forms.TextInput(attrs={
                'placeholder' : 'Mobile Number',
                'class': 'input-field'
            }),
            'region' : forms.TextInput(attrs={
                'placeholder' : 'Region',
                'class': 'input-field'
            }),
            'address' : forms.TextInput(attrs={
                'placeholder' : 'Address',
                'class': 'input-field'
            }),
            'occupation' : forms.TextInput(attrs={
                'placeholder' : 'Occupation',
                'class': 'input-field'
            }),
            'age' : forms.NumberInput(attrs={
                'placeholder' : 'Age',
                'class': 'input-field'
            }),

        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if '@' not in email or not email.endswith('.edu.ph'):
            raise ValidationError("Please enter a valid .edu.ph email address.")
        return email
    
# gawing basis
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        # ito names ng fields  magagamit yan pagtinawag mo {{ forms.email }} ->
        fields = ('email', 'password')
        # ganto maglagay ng class at placeholder ->
        widgets = {
            'password' : forms.PasswordInput(render_value=True, attrs={
                'placeholder': 'Password',
                'class': 'input-field'
            }),
            'email' : EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'input-field'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Email'
    

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profilePic',)

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('user', 'event', 'attended')

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('eventName', 'startDate', 'endDate', 'venue', 'address', 'eventDescription', 'pubmat', 'price', 'startTime', 'endTime')
        widgets = {
            'startDate': forms.DateInput(attrs={'type': 'date'}),
            'endDate': forms.DateInput(attrs={'type': 'date'}),
            'startTime': forms.DateInput(attrs={'type': 'time'}),
            'endTime': forms.DateInput(attrs={'type': 'time'}),
        }
        # required_fields = [list] to make the fields required
class EventRegistrationForm(forms.ModelForm):
    receipt_file = forms.FileField(required=True)

    class Meta:
        model = EventRegistration
        fields = ('event',)

    def __init__(self, user, event, *args, **kwargs):
        super(EventRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['start_date_of_event'] = forms.DateField(initial=event.startDate, disabled=True)

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
    
class MembershipRegistration(forms.ModelForm):
    class Meta:
        model = UserMembership
        fields = ('membership', 'verificationID', 'receipt')
    
    def __init__(self, user, membership, *args, **kwargs):
        super(MembershipRegistration, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['membership'] = forms.ModelChoiceField(queryset = MembershipTypes.objects.all(), initial=membership)
        self.fields['verificationID'].label = 'Identification'
