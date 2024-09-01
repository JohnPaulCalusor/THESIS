from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django import forms
# Create your models here.

class User(AbstractUser):
    mobileNum = models.CharField(max_length=16)
    region = models.CharField(max_length=32)
    address = models.CharField(max_length=32)
    occupation = models.CharField(max_length=16)
    age = models.IntegerField(null=True)
    memType = models.CharField(max_length=32)
    birthdate = models.DateField(null=True)
    verification_code = models.IntegerField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    profilePic = models.ImageField(upload_to="papsas_app/profilePic", null=True)

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membershipType = models.CharField(max_length=32)
    membershipDate = models.DateField()
    membershipExpireDate = models.DateField()
    membershipStatus = models.CharField(max_length=32)
    membershipPrice = models.DecimalField(max_digits=10, decimal_places=2)

class Election(models.Model):
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
        return f"{self.id} {self.candidate.first_name} ran candidacy for officer"
    
class Vote(models.Model):
    candidateID = models.ForeignKey(Candidacy, on_delete=models.CASCADE, related_name="candidates")
    voterID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voter")
    voteDate = models.DateField()

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

class Event(models.Model):
    eventName = models.CharField(max_length=32, null=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    venue = models.CharField(max_length=64, null=True)
    address = models.CharField(max_length=128, null=True)
    eventDescription = models.TextField(max_length=256, null=True)
    eventStatus = models.BooleanField(default=True)
    pubmat = models.ImageField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    startTime = models.TimeField(null=True)
    endTime = models.TimeField(null=True)
    audience = models.ManyToManyField(User, blank=True, related_name="spectator")


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    date_attended = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.eventName}"

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    receipt = models.BinaryField(null=True, blank=True) 
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} registered for {self.event.eventName} at {self.event.venue}"