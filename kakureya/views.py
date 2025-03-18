from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Product, CartItem
from django.db import IntegrityError
from django.utils import timezone
from .forms import ProductForm, UserRegisterForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile

def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserRegisterForm()
        })
    else:
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.save()
                login(request, user)
                return redirect('products')
            except IntegrityError:
                form.add_error(None, 'El usuario ya existe')
                return render(request, 'signup.html', {
                    'form': form,
                    'error': 'El usuario ya existe'
                })
        else:
            return render(request, 'signup.html', {
                'form': form,
                'error': 'Formulario inválido. Por favor, corrija los errores a continuación.'
            })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {
            "form": AuthenticationForm()
        })

    user = authenticate(
        request, username=request.POST["username"], password=request.POST["password"]
    )

    if user is None:
        return render(request, "signin.html", {
            "form": AuthenticationForm(),
            "error": "Usuario o contraseña incorrectos"
        })

    login(request, user)

    # Verifica si el usuario YA tiene un perfil antes de crearlo
    if not UserProfile.objects.filter(user=user).exists():
        try:
            UserProfile.objects.create(user=user, email=user.email)
        except IntegrityError:
            pass  # Maneja el error si el perfil ya existe

    return redirect("home")

@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = User.objects.exclude(username=request.user.username)
    grupos = Group.objects.all()

    if request.method == 'POST':
        if 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            user.delete()
            return redirect('user_management')

        elif 'assign_group' in request.POST:
            user_id = request.POST.get('user_id')
            group_id = request.POST.get('group_id')
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            user.groups.clear()
            user.groups.add(group)
            return redirect('user_management')

    return render(request, 'user_management.html', {'users': users, 'grupos': grupos})

@login_required
def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {
        'products': products
    })

@login_required
def products_added(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'products_added.html', {
        'cart_items': cart_items
    })

@login_required
def create_product(request):
    if request.method == 'GET':
        return render(request, 'create_product.html', {
            'form': ProductForm()
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
                'form': ProductForm(),
                'error': 'Campos invalidos'
            })

@login_required
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

@login_required
def add_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        product.added = timezone.now()
        product.save()
        return redirect('products')
    else:
        return render(request, 'add_product.html', {'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        product.delete()
        return redirect('products')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1
    else:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()

    messages.success(request, f'Se agregaron {quantity} unidades de "{product.name}" al carrito.')

    return redirect('products')