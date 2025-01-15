from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password

# Register your models here.

from .models import User, MembershipTypes, Vote, Candidacy, Officer, Election, Event, EventRegistration, UserMembership, Venue, Attendance, NewsandOffers, Achievement, EventRating

class UserAdmin(admin.ModelAdmin):
    list_display = ('id' ,'first_name', 'last_name', 'username','email_verified')
    search_fields = ['id__icontains', 'email']
    # disables admin to change anything
    # readonly_fields = ('password',)
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)  # Hash the password
        super().save_model(request, obj, form, change)

class EventRegistrationAdmin(admin.ModelAdmin):
    search_fields = ['id__icontains', 'user__email']

class UserMembershipAdmin(admin.ModelAdmin):
    search_fields = ['id__icontains', 'user__email']

# register user

admin.site.register(User, UserAdmin)
admin.site.register(MembershipTypes)
admin.site.register(UserMembership, UserMembershipAdmin)
admin.site.register(Vote)
admin.site.register(Candidacy)
admin.site.register(Officer)
admin.site.register(Election)
admin.site.register(Event)
admin.site.register(EventRating)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(Venue)
admin.site.register(Attendance)
admin.site.register(Achievement)
admin.site.register(NewsandOffers)