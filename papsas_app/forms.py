from django import forms
from .models import Attendance, EventRegistration, Event, User, UserMembership, MembershipTypes, Venue, Achievement, NewsandOffers, EventRating, Election
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, EmailInput
from django.utils import timezone

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'input-field',
        'required': True
            }
        )
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name','mobileNum', 'region', 'address', 'occupation', 'age', 'birthdate', 'institution')
        widgets = {
            'email' : forms.EmailInput(attrs={
                'placeholder' : 'Email',
                'class': 'input-field',
                'required' : True
            }),
            'birthdate' : forms.DateInput(attrs={
                'type': 'date',
                'placeholder' : 'Date of Birth',
                'class': 'input-field',
                'required' : True
            }),
            'first_name' : forms.TextInput(attrs={
                'placeholder' : 'First Name',
                'class': 'input-field',
                'required' : True
            }),
            'last_name' : forms.TextInput(attrs={
                'placeholder' : 'Last Name',
                'class': 'input-field',
                'required' : True
            }),
            'mobileNum' : forms.TextInput(attrs={
                'placeholder' : 'Mobile Number',
                'class': 'input-field',
                'required' : True
            }),
            'address' : forms.TextInput(attrs={
                'placeholder' : 'Address',
                'class': 'input-field',
                'required' : True
            }),
            'age' : forms.NumberInput(attrs={
                'placeholder' : 'Age',
                'class': 'input-field',
                'required' : True
            }),
            'institution' : forms.TextInput(attrs={
                'placeholder' : 'Institution',
                'class': 'input-field',
                'required' : True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['birthdate'].label = 'Date of Birth'
        self.fields['region'].widget.attrs['class'] = 'input-field'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Optionally add password strength validation here
        return password

    def clean_your_number(self):
        data = self.cleaned_data['mobileNum']
        try:
            integer_value = int(data)
        except ValueError:
            raise forms.ValidationError("This field must be an integer.")
        return integer_value

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
    
class EventRatingForm(forms.ModelForm):
    class Meta:
        model = EventRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)], 
                                        attrs={'class': 'horizontal-radio'}),
            'comment': forms.Textarea(attrs={'rows': 6}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profilePic',)

class TORForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('tor',)

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('attended',)

occupation = [
    ('Student', 'Student'),
    ('Practitioner', 'Practitioner'),
]

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('eventName', 'startDate', 'endDate', 'venue', 'exclusive', 'eventDescription', 'pubmat', 'price', 'startTime', 'endTime')
        widgets = {
            'startDate': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat()  # Set minimum date to today
            }),
            'endDate': forms.DateInput(attrs={'type': 'date'}),
            'startTime': forms.DateInput(attrs={'type': 'time'}),
            'endTime': forms.DateInput(attrs={'type': 'time'}),
        }

    def clean_pubmat(self):
        pubmat = self.cleaned_data.get('pubmat')
        if self.instance and self.instance.pk is not None:  # If updating
            # If no new image uploaded, we do not raise an error
            return pubmat
        if not pubmat:  # If no image uploaded during creation
            raise forms.ValidationError("Image is required when creating a new achievement.")
        return pubmat
    
class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['user', 'event', 'receipt', 'reference_number']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        event = kwargs.pop('event', None)
        super(EventRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['amount'] = forms.IntegerField(initial=event.price, disabled=True)
        self.fields['receipt'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['reference_number'].widget.attrs.update({'class': 'form-control'})

        self.fields['user'] = forms.ModelChoiceField(
            queryset=User.objects.all(),
            initial=user,
            widget=forms.HiddenInput()
        )
        self.fields['event'] = forms.ModelChoiceField(
            queryset=Event.objects.all(),
            initial=event,
            widget=forms.HiddenInput()
        )

    def clean_reference_number(self):
        reference_number = self.cleaned_data.get('reference_number')
        if reference_number is not None and reference_number <= 0:
            raise forms.ValidationError("Reference number must be a positive integer.")
        return reference_number
    
class MembershipRegistration(forms.ModelForm):
    class Meta:
        model = UserMembership
        fields = ('membership', 'verificationID', 'receipt', 'reference_number')
    
    def __init__(self, user, membership, *args, **kwargs):
        super(MembershipRegistration, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['membership'] = forms.ModelChoiceField(queryset = MembershipTypes.objects.all(), initial=membership)
        self.fields['verificationID'].label = 'Identification'
        self.fields['membership'].disabled = True

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ('name', 'address', 'capacity')

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ('title', 'endDate', 'numWinners')


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ('name', 'description', 'pubmat')
    def clean_pubmat(self):
        pubmat = self.cleaned_data.get('pubmat')
        if self.instance and self.instance.pk is not None:  # If updating
            # If no new image uploaded, we do not raise an error
            return pubmat
        if not pubmat:  # If no image uploaded during creation
            raise forms.ValidationError("Image is required when creating a new achievement.")
        return pubmat

class NewsForm(forms.ModelForm):
    class Meta:
        model = NewsandOffers
        fields = ('name', 'description', 'pubmat')
    def clean_pubmat(self):
        pubmat = self.cleaned_data.get('pubmat')
        if self.instance and self.instance.pk is not None:  # If updating
            # If no new image uploaded, we do not raise an error
            return pubmat
        if not pubmat:  # If no image uploaded during creation
            raise forms.ValidationError("Image is required when creating a new achievement.")
        return pubmat

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'mobileNum', 'region', 'address', 'occupation', 'age', 'birthdate', 'institution')
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'input-field'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'class': 'input-field'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'input-field'
            }),
            'mobileNum': forms.TextInput(attrs={
                'placeholder': 'Mobile Number',
                'class': 'input-field'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Address',
                'class': 'input-field'
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': 'Age',
                'class': 'input-field'
            }),
            'birthdate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input-field'
            }),
            'institution': forms.TextInput(attrs={
                'placeholder': 'Institution',
                'class': 'input-field'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['birthdate'].label = 'Date of Birth'
        self.fields['region'].widget.attrs['class'] = 'input-field'    
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('mobileNum', 'region', 'address', 'occupation', 'institution', 'profilePic', 'tor')
        widgets = {
            'mobileNum': forms.TextInput(attrs={
                'placeholder': 'Mobile Number',
                'class': 'input-field'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Address',
                'class': 'input-field'
            }),
            'institution': forms.TextInput(attrs={
                'placeholder': 'Institution',
                'class': 'input-field'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['region'].widget.attrs['class'] = 'input-field'    

