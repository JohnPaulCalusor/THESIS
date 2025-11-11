from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password

# Register your models here.

from .models import User, MembershipTypes, Vote, Candidacy, Officer, Election, Event, EventRegistration, UserMembership, Venue, Attendance, NewsandOffers, Achievement, EventRating
from .models_position import Position

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

class ElectionAdminForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = "__all__"
        label_suffix = ""
        labels = {
            "numWinners": "At-large winner cap (leave blank/zero to use per-position winners)"
        }
        help_texts = {
            "numWinners": "At-large winner cap (leave blank/zero to use per-position winners)"
        }

class ElectionAdmin(admin.ModelAdmin):
    form = ElectionAdminForm

class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'election', 'title', 'winners', 'enabled', 'sort')
    list_editable = ('winners',)
    list_filter = ('election', 'enabled')

# register user

admin.site.register(User, UserAdmin)
admin.site.register(MembershipTypes)
admin.site.register(UserMembership, UserMembershipAdmin)
admin.site.register(Vote)
admin.site.register(Candidacy)
admin.site.register(Officer)
admin.site.register(Election, ElectionAdmin)
admin.site.register(Event)
admin.site.register(EventRating)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(Venue)
admin.site.register(Attendance)
admin.site.register(Achievement)
admin.site.register(NewsandOffers)
admin.site.register(Position, PositionAdmin)
