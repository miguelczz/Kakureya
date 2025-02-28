from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import IntegrityError
from .forms import ProductForm
from .models import Product


def home(request):

    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1']
                )

                user.save()
                login(request, user)
                return redirect('tasks')

            except IntegrityError:
                return render(request, 'signup.html', {
                    'myform': UserCreationForm,
                    'error': 'El usuario ya existe'
                })

        return render(request, 'signup.html', {
            'myform': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })


def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {
        'products': products
    })


def create_product(request):
    if request.method == 'GET':
        return render(request, 'create_product.html', {
            'form': ProductForm
        })
    elif request.method == 'POST':
        try:
            form = ProductForm(request.POST)
            new_product = form.save(commit=False)
            new_product.user = request.user
            new_product.save()
            return redirect('products')
        except ValueError:
            return render(request, 'create_product.html', {
                'form': ProductForm,
                'error': 'Campos invalidos'
            })


def product_detail(request, product_id):
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=product_id)
        form = ProductForm(instance=product)
        return render(request, 'product_detail.html', {'product': product, 'form': form})
    else:
        try:
            product = get_object_or_404(Product, pk=product_id)
            form = ProductForm(request.POST, instance=product)
            form.save()
            return redirect('products')
        except ValueError:
            return render(request, 'product_detail.html', {
                'product': product,
                'form': form,
                'error': 'Campos invalidos'
            })


def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password']
        )

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'
            })
        else:
            login(request, user)
            return redirect('home')
