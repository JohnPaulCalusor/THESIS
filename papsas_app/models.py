from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django import forms
from django.db.models import F
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
# Create your models here.

Regions = [
    ('Region', 'Region'),
    ('National Capital Region', 'NCR'),
    ('Cordillera Administrative Region', 'CAR'),
    ('Ilocos Region', 'Region I'),
    ('Cagayan Valley', 'Region II'),
    ('Central Luzon', 'Region III'),
    ('Calabarzon', 'Region IV-A'),
    ('Mimaropa', 'Region IV-B'),
    ('Bicol Region', 'Region V'),
    ('Western Visayas', 'Region VI'),
    ('Central Visayas', 'Region VII'),
    ('Eastern Visayas', 'Region VIII'),
    ('Zamboanga Peninsula', 'Region IX'),
    ('Northern Mindanao', 'Region X'),
    ('Davao Region', 'Region XI'),
    ('Soccsksargen', 'Region XII'),
    ('Caraga', 'Region XIII'),
    ('Bangsamoro Autonomous Region in Muslim Mindanao', 'BARMM')
]

occupation = [
    ('Student', 'Student'),
    ('Practitioner', 'Practitioner'),
]

status = [
    ('Approved', 'Approved'),
    ('Pending', 'Pending'),
    ('Declined', 'Declined')
]



class User(AbstractUser):
    mobileNum = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='Mobile number must be 11 digits.'
            )
        ]
    )
    region = models.CharField(max_length=64, choices=Regions, default='Region',)
    address = models.CharField(max_length=32)
    occupation = models.CharField(max_length=16, choices=occupation, default='Occupation')
    age = models.IntegerField(
        null=True,
        validators=[
            MinValueValidator(18, message="Age must be at least 18."),
            MaxValueValidator(100, message="Age must be less than or equal to 100.")
        ]
    )
    birthdate = models.DateField(null=True, blank=True)
    verification_code = models.IntegerField(null=True, blank=True)
    verification_code_expiration = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    profilePic = models.ImageField(null=True, blank=True, upload_to="papsas_app/profilePic", default="papsas_app/images/default_dp.jpeg")
    institution = models.CharField(max_length=128, null=True)

    def get_expiration_timestamp(self):
        return int(self.verification_code_expiration.timestamp()) if self.verification_code_expiration else None

    def __str__(self):
        return f'{self.id} - {self.first_name}'

    def save(self, *args, **kwargs):
        if self.verification_code:
            if not self.verification_code_expiration or timezone.now() > self.verification_code_expiration:
                self.verification_code_expiration = timezone.now() + timezone.timedelta(minutes=2)
        else:
            self.verification_code = None
            self.verification_code_expiration = None
        super().save(*args, **kwargs)


class MembershipTypes(models.Model):
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/event", null=True)
    type = models.CharField(max_length=16, null=True)
    description = models.CharField(max_length=512, null=True)
    duration = models.DurationField(null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.type}'
    
class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member')
    membership = models.ForeignKey(MembershipTypes, on_delete=models.CASCADE)
    registrationDate = models.DateField(auto_now_add=True)
    expirationDate = models.DateField(null=True, blank=True)
    receipt = models.ImageField(upload_to="papsas_app/reciept", null=True, blank=True) 
    reference_number = models.IntegerField(null=True)
    verificationID = models.ImageField(upload_to="papsas_app/verificationID", null=True, blank=True) 
    membershipVerification = models.BooleanField(default=False)

    def __str__ (self):
        return f'{self.user.id} : {self.user.first_name} - {self.id} : {self.membership}'

class Election(models.Model):
    title = models.CharField(max_length=128, null=True)    
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    electionStatus = models.BooleanField()
    numWinners = models.IntegerField(null=True)

    def __str__(self):
        return f'Election {self.id}'

class Candidacy(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="candidate")
    candidacyStatus = models.BooleanField(null=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="elections")
    
    def __str__(self):
        return f"{self.candidate.first_name} running for Election {self.election.title} {self.election.startDate.year}"
    
class Vote(models.Model):
    candidateID = models.ManyToManyField(Candidacy, related_name="nominee")
    voterID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voter")
    voteDate = models.DateField(auto_now_add=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, null=True, related_name="poll")

    def __str__(self):
        return f'{self.candidateID.all()}'

class Officer(models.Model):
    candidateID = models.ForeignKey(Candidacy, on_delete=models.CASCADE, related_name="officers")
    position = models.CharField(max_length=32, choices=[
        ('President', 'President'),
        ('Secretary', 'Secretary'),
        ('Regular', 'Regular')
    ], null=True)
    termStart = models.DateField(null=True)
    termEnd = models.DateField(null=True)
    
    def __str__(self):
        return f"{self.candidateID.candidate.first_name} was elected ({self.termStart} - {self.termEnd})"

class Venue(models.Model):
    name = models.CharField(max_length=32, null=True)
    address = models.CharField(max_length=64, null=True)
    capacity = models.IntegerField()

    def __str__(self):
        return f'{self.name}'


class Event(models.Model):
    eventName = models.CharField(max_length=32, null=True)
    exclusive = models.BooleanField(default=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, null=True)
    eventDescription = models.TextField(max_length=9999, null=True)
    eventStatus = models.BooleanField(default=True)
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/event", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    startTime = models.TimeField(null=True)
    endTime = models.TimeField(null=True)
    postStamp = models.DateTimeField(auto_now_add=True, null=True) #date na pinost

    def __str__(self):
        return f'{self.id} - {self.eventName}'
    
    def short_description(self):
        if len(self.description) > 100:
            return f'{self.description[:100]}...'
        return self.description
    
class Achievement(models.Model):
    name = models.CharField(max_length=32, null=True)
    description = models.TextField(max_length=9999, null=True)
    postStamp = models.DateTimeField(auto_now_add=True)
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/achievement", null=True, blank=True)

    def __str__(self):
        return f'{self.id} - {self.name}'
    
    def short_description(self):
        if len(self.description) > 100:
            return f'{self.description[:100]}...'
        return self.description
        
class NewsandOffers(models.Model):
    name = models.CharField(max_length=32, null=True)
    description = models.TextField(max_length=9999, null=True)
    postStamp = models.DateTimeField(auto_now_add=True, null=True)
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/newsandoffers", null=True, blank=True)

    def short_description(self):
        if len(self.description) > 100:
            return f'{self.description[:100]}...'
        return self.description
    
class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="activity")
    receipt = models.ImageField(upload_to="papsas_app/reciept", null=True, blank=True) 
    reference_number = models.IntegerField(null = True)
    registered_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=10, choices=status, default='Pending')

    def __str__(self):
        return f"{self.id} : {self.user.id} : {self.user.username} - {self.event.eventName} at {self.event.venue}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audience')
    event = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    date_attended = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} attended {self.event.event.eventName}"
    
