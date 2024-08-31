from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .models import User, Membership, Vote, Candidacy, Officer, Election, Event

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email_verified')

# register user

admin.site.register(User, UserAdmin) 
admin.site.register(Membership)
admin.site.register(Vote)
admin.site.register(Candidacy)
admin.site.register(Officer)
admin.site.register(Election)
admin.site.register(Event)