from django.contrib import admin
from .models import Message  # ← 這是重點

admin.site.register(Message)

