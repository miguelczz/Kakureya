from django.contrib import admin
from .models import UserProfile, Product, CartItem, Payment

# Personalización del panel
admin.site.site_header = "Administración Kakureya"
admin.site.site_title = "Admin Kakureya"
admin.site.index_title = "Administración de la Tienda Oculta"

# Admin para UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'email', 'phone_number']
    list_filter = ['user__is_active']

# Admin para Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ['name', 'description']
    list_filter = ['category', 'created_at', 'updated_at']
    list_display = ['name', 'category', 'price', 'stock', 'user']

# Admin para CartItem
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'product__name']
    list_filter = ['added_at']
    list_display = ['product', 'user', 'quantity', 'added_at']

# Admin para Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'transaction_id']
    list_filter = ['payment_method', 'status', 'created_at']
    list_display = ['transaction_id', 'user', 'amount', 'payment_method', 'status']
