from django.contrib import admin
from .models import CustomUser  # ← 這是重點

class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'date_joined')
	ordering = ('-date_joined',)
	search_fields = ('username', 'email', 'phone') # 可搜尋欄位

admin.site.register(CustomUser, UserAdmin)
