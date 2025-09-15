from django.contrib import admin
from .models import financial_info

# Register your models so they will appear inside admin panel so we can view them.

admin.site.register(financial_info)