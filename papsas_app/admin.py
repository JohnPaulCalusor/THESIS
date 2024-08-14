from django.contrib import admin

# Register your models here.

from .models import User

# register user
admin.site.register(User) 