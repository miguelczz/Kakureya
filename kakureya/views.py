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
from .models import Payment
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

def home(request):
    return render(request, 'home.html')

# 🟢 Improved signup function
def signup(request):
    if request.method == "GET":
        return render(request, "signup.html", {"form": UserRegisterForm()})

    form = UserRegisterForm(request.POST)
    if form.is_valid():
        try:
            user = form.save()
            UserProfile.objects.get_or_create(user=user, email=user.email)  # Ensure profile exists
            login(request, user)
            return redirect("products")
        except IntegrityError:
            form.add_error(None, "El usuario ya existe")

    return render(request, "signup.html", {"form": form, "error": "Formulario inválido."})

@login_required
def signout(request):
    logout(request)
    return redirect('home')

# 🟢 Improved signin function
def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm()})

    user = authenticate(
        request, username=request.POST.get("username"), password=request.POST.get("password")
    )

    if user is None:
        return render(request, "signin.html", {"form": AuthenticationForm(), "error": "Usuario o contraseña incorrectos"})

    login(request, user)

    # Ensure user profile exists
    UserProfile.objects.get_or_create(user=user, email=user.email)

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

# 🟢 Improved product creation with image support
@login_required
def create_product(request):
    if request.method == "GET":
        return render(request, "create_product.html", {"form": ProductForm()})

    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        return redirect("products")


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

# 🟢 Improved stock validation when adding products to the cart
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('signup')

    product = get_object_or_404(Product, id=product_id)

    # Verificar disponibilidad de stock
    if product.stock < 1:
        messages.error(request, f"{product.name} está agotado.")
        return redirect("products")

    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1

    # No permitir cantidades menores a 1
    quantity = max(1, quantity)

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.quantity = min(quantity, product.stock)
    else:
        # No permitir que el total supere el stock disponible
        if cart_item.quantity + quantity <= product.stock:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = product.stock

    cart_item.save()

    messages.success(request, f"{product.name} añadido al carrito.")
    return redirect("cart")

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.delete()
    
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('cart')

@login_required
def cart_summary(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)

    return render(request, 'cart_summary.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        transaction_id = str(uuid.uuid4())
        
        payment = Payment.objects.create(
            user=request.user,
            amount=total_amount,
            payment_method=payment_method,
            status="pending",
            transaction_id=transaction_id,
            )

        if payment_method == "paypal":
            paypal_dict = {
                "business": "your-paypal-business-email@example.com",
                "amount": "{:.2f}".format(total_amount), 
                "item_name": f"Order {transaction_id}",
                "invoice": transaction_id,
                "currency_code": "USD",
                "notify_url": request.build_absolute_uri(reverse("paypal-ipn")),
                "return_url": request.build_absolute_uri(reverse("payment_success", args=[payment.id])),
                "cancel_return": request.build_absolute_uri(reverse("payment_failed", args=[payment.id])),
            }
            form = PayPalPaymentsForm(initial=paypal_dict)
            return render(request, "checkout.html", {"cart_items": cart_items, "total_amount": total_amount, "form": form})
        
        elif payment_method == "credit_card":
            # Pago en tarjeta de credito a ser implementado.
            return redirect("credit_card_payment", payment_id=payment.id)
        
        elif payment_method == "cash":
            # Mark order as "Cash on Delivery"
            payment.status = "pending (cash)"
            payment.save()
            messages.success(request, "Tu pedido ha sido registrado. Paga al recibir.")
            return redirect("home")

    return render(request, "checkout.html", {"cart_items": cart_items, "total_amount": total_amount, "form": None})

@login_required
def payment_success(request, payment_id):
    """ Handle successful payments from PayPal """
    payment = get_object_or_404(Payment, id=payment_id)

    # Update payment status
    payment.status = "completed"
    payment.save()

    # Clear user's cart after successful payment
    CartItem.objects.filter(user=request.user).delete()

    messages.success(request, "Payment successful! Your order has been placed.")
    return redirect("home")


@login_required
def payment_failed(request, payment_id):
    """ Handle failed payments """
    payment = get_object_or_404(Payment, id=payment_id)

    # Update payment status
    payment.status = "failed"
    payment.save()

    messages.error(request, "Payment failed. Please try again.")
    return redirect("checkout")

PAYPAL_VERIFY_URL = "https://api-m.sandbox.paypal.com/v2/checkout/orders/"

# Get your PayPal API credentials
PAYPAL_CLIENT_ID = "YOUR_PAYPAL_CLIENT_ID"
PAYPAL_SECRET = "YOUR_PAYPAL_SECRET"

# 🟢 Securely retrieve PayPal access token
def get_paypal_access_token():
    response = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    return response.json().get("access_token") if response.status_code == 200 else None



@csrf_exempt  # Since it's an AJAX request
@login_required
def payment_capture(request):
    if request.method == "POST":
        data = json.loads(request.body)
        transaction_id = data.get("transaction_id")

        if not transaction_id:
            return JsonResponse({"error": "Invalid request"}, status=400)

        # Get PayPal access token
        access_token = get_paypal_access_token()
        if not access_token:
            return JsonResponse({"error": "Failed to get PayPal token"}, status=500)

        # Verify transaction with PayPal
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(f"{PAYPAL_VERIFY_URL}{transaction_id}", headers=headers)

        if response.status_code == 200:
            payment_data = response.json()

            # Ensure transaction is completed
            if payment_data.get("status") == "COMPLETED":
                amount_paid = payment_data["purchase_units"][0]["amount"]["value"]

                # Check if payment exists in our database
                payment, created = Payment.objects.get_or_create(
                    transaction_id=transaction_id,
                    defaults={
                        "user": request.user,
                        "amount": amount_paid,
                        "payment_method": "paypal",
                        "status": "completed",
                    },
                )

                # If the payment was already in the database, just update its status
                if not created:
                    payment.status = "completed"
                    payment.save()

                return JsonResponse({"payment_id": payment.id})

        return JsonResponse({"error": "Payment verification failed"}, status=400)