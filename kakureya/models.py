import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("sushi", "Sushi"),
        ("ramen", "Ramen"),
        ("yakitori", "Yakitori"),
        ("donburi", "Donburi"),
        ("postres", "Postres"),
        ("sin categoría", "Sin categoría"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    stock = models.IntegerField(default=10)
    image = models.ImageField(upload_to='products', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Sin categoría")

    def __str__(self):
        return f"{self.name} (por {self.user.username if self.user else 'Anónimo'})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity}x {self.product.name} - {self.user.username}"

    class Meta:
        unique_together = ('user', 'product')  # Avoid duplicate items
        verbose_name = "Item del carrito"
        verbose_name_plural = "Ítems del carrito"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('paypal', 'PayPal'),
        ('credit_card', 'Tarjeta de Crédito'),
        ('cash', 'Efectivo'),
    ]
    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='paypal')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=False)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago {self.transaction_id} - {self.status} (${self.amount})"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"