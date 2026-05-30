from django.contrib import admin

from .models import Product, Stock, Order

admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Order)