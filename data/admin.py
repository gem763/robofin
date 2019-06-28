from django.contrib import admin
from .models import Asset, Marketdata, Coin

# Register your models here.
admin.site.register(Asset)
admin.site.register(Marketdata)
admin.site.register(Coin)
