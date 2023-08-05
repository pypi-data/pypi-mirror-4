from django.contrib import admin
from models import Currency, ExchangeRate


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'current_rate', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('code', 'name') 

class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'date', 'rate')
    list_filter = ('date',)
    search_fields = ('currency__code', 'currency__name') 

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(ExchangeRate, ExchangeRateAdmin)
