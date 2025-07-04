# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=15, blank=True, unique=True)
    birthday = models.DateField(null=True, blank=True)

    email = models.EmailField(unique=True) 

    def __str__(self):
        return self.username

