from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Product(models.Model):

    CATEGORY_CHOICES = [
        ("sushi", "Sushi"),
        ("ramen", "Ramen"),
        ("yakitori", "Yakitori "),
        ("donburi", "Donburi"),
        ("postres", "Postres"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=0)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="Sin categoría"
    )

    def __str__(self):
        return self.name + ' by ' + self.user.username
