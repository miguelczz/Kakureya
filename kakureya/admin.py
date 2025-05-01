from django.contrib import admin
from .models import Product, UserProfile, Sale, SaleItem, CartItem

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'category', 'price', 'stock', 'user')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone_number')
    search_fields = ('user__username', 'email', 'phone_number')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_sale')
    
    def has_delete_permission(self, request, obj=None):
        return False  # Impedir eliminar ítems de venta para mantener la integridad

class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SaleItemInline]
    
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'status', 'address')
        }),
        ('Información adicional', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Acciones para cambiar el estado de las ventas
    actions = ['mark_as_preparing', 'mark_as_shipping', 'mark_as_delivered', 'mark_as_canceled']
    
    def mark_as_preparing(self, request, queryset):
        queryset.update(status='preparing')
        self.message_user(request, f"{queryset.count()} ventas marcadas como 'En preparación'")
    mark_as_preparing.short_description = "Marcar como 'En preparación'"
    
    def mark_as_shipping(self, request, queryset):
        queryset.update(status='shipping')
        self.message_user(request, f"{queryset.count()} ventas marcadas como 'En camino'")
    mark_as_shipping.short_description = "Marcar como 'En camino'"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f"{queryset.count()} ventas marcadas como 'Entregado'")
    mark_as_delivered.short_description = "Marcar como 'Entregado'"
    
    def mark_as_canceled(self, request, queryset):
        queryset.update(status='canceled')
        self.message_user(request, f"{queryset.count()} ventas marcadas como 'Cancelado'")
    mark_as_canceled.short_description = "Marcar como 'Cancelado'"

# Registrar los modelos con sus clases admin personalizadas
admin.site.register(Product, ProductAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Sale, SaleAdmin)