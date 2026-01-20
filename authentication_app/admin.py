from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Registriert den CustomUser mit den Standard-Funktionen für User
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass