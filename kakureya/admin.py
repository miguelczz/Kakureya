from django.contrib import admin
from .models import Product


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Product, ProductAdmin)
