from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model where the email is the unique identifier for authentication
    instead of the username.
    """
    email = models.EmailField(unique=True)

    # We use the email as the primary identifier for login
    USERNAME_FIELD = 'email'
    
    # Username is still required by Django internally, but we can make it secondary
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email