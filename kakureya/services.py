from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import timezone
from .models import Product
from .forms import ProductForm

# User Authentication Service
def register_user(request):
    if request.POST['password1'] == request.POST['password2']:
        try:
            user = User.objects.create_user(
                username=request.POST['username'], password=request.POST['password1']
            )
            user.save()
            login(request, user)
            return None  # No error
        except IntegrityError:
            return 'El usuario ya existe'
    return 'Las contraseñas no coinciden'

def authenticate_user(request):
    user = authenticate(
        request, username=request.POST['username'], password=request.POST['password']
    )
    return user  # Returns None if authentication fails

def logout_user(request):
    logout(request)

# Product Management Service
def get_all_products():
    return Product.objects.all()

def get_added_products():
    return Product.objects.filter(added__isnull=False).order_by('-added')

def create_product(request):
    form = ProductForm(request.POST)
    if form.is_valid():
        new_product = form.save(commit=False)
        new_product.user = request.user
        new_product.save()
        return None  # No error
    return 'Campos inválidos'

def get_product_by_id(product_id):
    return Product.objects.filter(id=product_id).first()

def update_product(request, product):
    form = ProductForm(request.POST, instance=product)
    if form.is_valid():
        form.save()
        return None  # No error
    return 'Campos inválidos'

def delete_product(product):
    product.delete()

# Product State Management Service
def add_product(product):
    product.added = timezone.now()
    product.save()

def quit_product(product):
    product.added = None
    product.save()
