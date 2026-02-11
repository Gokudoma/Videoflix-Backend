from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Registers the CustomUser with the standard user functions
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass