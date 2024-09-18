from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django import forms
from django.db.models import F
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

class User(AbstractUser):
    mobileNum = models.CharField(max_length=11)
    region = models.CharField(max_length=64, choices=Regions, default = 'Region',)
    address = models.CharField(max_length=32)
    occupation = models.CharField(max_length=16)
    age = models.IntegerField(null=True)
    birthdate = models.DateField(null=True)
    verification_code = models.IntegerField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    profilePic = models.ImageField(null=True, blank=True, upload_to="papsas_app/profilePic", default="papsas_app/profilePic/default_dp.jpeg") 
    institution = models.CharField(max_length=128, null=True)

    def __str__(self):
        return f'{self.id} - {self.first_name}'

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
    verificationID = models.ImageField(upload_to="papsas_app/verificationID", null=True, blank=True) 
    membershipVerification = models.BooleanField(default=False)

    def __str__ (self):
        return f'{self.membership}'

class Election(models.Model):
    title = models.CharField(max_length=128, null=True)    
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    electionStatus = models.BooleanField()

    def __str__(self):
        return f'Election {self.id}'

class Candidacy(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="candidate")
    candidacyStatus = models.BooleanField(null=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="elections")
    
    def __str__(self):
        return f"{self.id} - {self.candidate.first_name} : officer"
    
class Vote(models.Model):
    candidateID = models.ManyToManyField(Candidacy, related_name="nominee")
    voterID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voter")
    voteDate = models.DateField(auto_now_add=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, null=True)

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
        return f"{self.candidateID.candidate.first_name} - {self.candidateID.candidate.id} is appointed as {self.position}"

class Venue(models.Model):
    name = models.CharField(max_length=32, null=True)
    address = models.CharField(max_length=64, null=True)
    capacity = models.IntegerField()

    def __str__(self):
        return f'{self.name}'


class Event(models.Model):
    eventName = models.CharField(max_length=32, null=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, null=True)
    eventDescription = models.TextField(max_length=9999, null=True)
    eventStatus = models.BooleanField(default=True)
    pubmat = models.ImageField(upload_to="papsas_app/pubmat/event", null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    startTime = models.TimeField(null=True)
    endTime = models.TimeField(null=True)

    def __str__(self):
        return f'{self.id} - {self.eventName}'

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    receipt = models.ImageField(upload_to="papsas_app/reciept", null=True, blank=True) 
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.eventName} at {self.event.venue}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audience')
    event = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    date_attended = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.event}"
    
