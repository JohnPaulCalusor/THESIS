from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password

# Register your models here.

from .models import User, MembershipTypes, Vote, Candidacy, Officer, Election, Event, EventRegistration, UserMembership, Venue, Attendance, NewsandOffers, Achievement, EventRating

class UserAdmin(admin.ModelAdmin):
    list_display = ('id' ,'first_name', 'username','email_verified')
    # disables admin to change anything
    # readonly_fields = ('password',)
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)  # Hash the password
        super().save_model(request, obj, form, change)

# register user

admin.site.register(User, UserAdmin)
admin.site.register(MembershipTypes)
admin.site.register(UserMembership)
admin.site.register(Vote)
admin.site.register(Candidacy)
admin.site.register(Officer)
admin.site.register(Election)
admin.site.register(Event)
admin.site.register(EventRating)
admin.site.register(EventRegistration)
admin.site.register(Venue)
admin.site.register(Attendance)
admin.site.register(Achievement)
admin.site.register(NewsandOffers)