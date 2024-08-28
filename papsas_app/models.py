from django.db import models
from django.contrib.auth.models import AbstractUser

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
