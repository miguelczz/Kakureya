from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Product
from .forms import ProductForm

# User Authentication Service
def register_user(request):
    # Check if passwords match
    if request.POST['password1'] == request.POST['password2']:
        try:
            # Create the user
            user = User.objects.create_user(
                username=request.POST['username'], password=request.POST['password1']
            )
            user.save()
            login(request, user)
            return None  # No error
        except IntegrityError:
            # If username already exists, raise a validation error
            raise ValidationError('El usuario ya existe')
    return 'Las contraseñas no coinciden'

def authenticate_user(request):
    # Authenticate the user with provided credentials
    user = authenticate(
        request, username=request.POST['username'], password=request.POST['password']
    )
    return user  # Returns None if authentication fails

def logout_user(request):
    # Log the user out
    logout(request)

# Product Management Service
def get_all_products():
    # Get all products
    return Product.objects.all()

def get_added_products():
    # Get products that have been added, ordered by added date
    return Product.objects.filter(added__isnull=False).order_by('-added')

def create_product(request):
    form = ProductForm(request.POST)
    if form.is_valid():
        new_product = form.save(commit=False)
        new_product.user = request.user
        new_product.save()
        return None  # No error
    # Return form validation errors for detailed feedback
    return form.errors

def get_product_by_id(product_id):
    # Get product by ID, returns None if not found
    return Product.objects.filter(id=product_id).first()

def update_product(request, product):
    form = ProductForm(request.POST, instance=product)
    if form.is_valid():
        form.save()
        return None  # No error
    # Return form validation errors for detailed feedback
    return form.errors

def delete_product(product):
    # Delete the product (cascades if necessary)
    product.delete()

# Product State Management Service
def add_product(product):
    # Add product and set the 'added' timestamp if it's not already set
    if not product.added:
        product.added = timezone.now()
        product.save()

def quit_product(product):
    # Set 'added' to None when quitting the product
    product.added = None
    product.save()
