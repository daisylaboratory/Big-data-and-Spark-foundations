from django.contrib import admin

# Register your models here.

from .models import SalesByCardType, SalesByCountry

admin.site.register(SalesByCardType)
admin.site.register(SalesByCountry)
