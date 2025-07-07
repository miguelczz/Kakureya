# Definición de modelos base para usuarios, productos, ventas, carrito y reseñas

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.module_loading import import_string

# --- Perfil de usuario extendido ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(max_length=255, blank=True, null=True)
    second_last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    dni = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.user.email

# --- Productos disponibles ---
class Product(models.Model):
    CATEGORY_CHOICES = [
        ("sushi", "Sushi"),
        ("ramen", "Ramen"),
        ("yakitori", "Yakitori"),
        ("donburi", "Donburi"),
        ("postres", "Postres"),
        ("bebidas", "Bebidas"),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products', null=True, blank=True, storage=import_string(settings.DEFAULT_FILE_STORAGE)())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Sin categoría")

    def __str__(self):
        return "{} (por {})".format(self.name, self.user.username if self.user else "Anónimo")

# --- Ítems en el carrito ---
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} en el carrito de {}".format(self.product.name, self.user.username)

    class Meta:
        unique_together = ('user', 'product')

# --- Ventas realizadas ---
class Sale(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'En preparación'),
        ('shipping', 'En camino'),
        ('delivered', 'Entregado'),
        ('canceled', 'Cancelado'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    address = models.TextField(verbose_name="Dirección de entrega")

    # Información de pago
    payment_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Venta #{} - {} - {}".format(self.id, self.user.username, self.get_status_display())

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())

    def get_items_count(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-created_at']

# --- Detalle de productos vendidos ---
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return "{} x {}".format(self.quantity, self.product.name)

    def get_total(self):
        return self.price_at_sale * self.quantity

    class Meta:
        verbose_name = "Ítem de venta"
        verbose_name_plural = "Ítems de venta"

# --- Opiniones de usuarios ---
class Review(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    profesion = models.CharField(max_length=100)
    comentario = models.TextField()
    calificacion = models.FloatField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    def estrellas_completas(self):
        return int(self.calificacion)

    def media_estrella(self):
        return self.calificacion - int(self.calificacion) >= 0.5