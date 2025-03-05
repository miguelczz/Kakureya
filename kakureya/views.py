from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .services import (
    register_user, authenticate_user, logout_user,
    get_all_products, get_added_products, create_product,
    get_product_by_id, update_product, delete_product,
    add_product, quit_product
)
from .forms import ProductForm

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})  # Instantiate the form correctly
    else:
        error = register_user(request)
        if error:
            return render(request, 'signup.html', {'form': UserCreationForm(), 'error': error})  # Same here
        return redirect('products')

@login_required
def products(request):
    return render(request, 'products.html', {'products': get_all_products()})

@login_required
def products_added(request):
    return render(request, 'products.html', {'products': get_added_products()})

@login_required
def create_product_view(request):
    if request.method == 'GET':
        return render(request, 'create_product.html', {'form': ProductForm()})  # Instantiate the form correctly
    else:
        error = create_product(request)
        if error:
            return render(request, 'create_product.html', {'form': ProductForm(), 'error': error})  # Same here
        return redirect('products')

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'GET':
        return render(request, 'product_detail.html', {'product': product, 'form': ProductForm(instance=product)})
    else:
        error = update_product(request, product)
        if error:
            return render(request, 'product_detail.html', {'product': product, 'form': ProductForm(instance=product), 'error': error})
        return redirect('products')

@login_required
def add_product_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        add_product(product)
        return redirect('products')

@login_required
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        delete_product(product)
        return redirect('products')

@login_required
def quit_product_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        quit_product(product)
        return redirect('products_added')

def signout(request):
    logout_user(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm()})  # Instantiate the form correctly
    else:
        user = authenticate_user(request)
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm(), 'error': 'Usuario o contraseña incorrectos'})  # Same here
        login(request, user)
        return redirect('home')
