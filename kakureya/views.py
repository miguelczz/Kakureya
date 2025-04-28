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
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.conf import settings

def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

def home(request):
    return render(request, 'home.html')

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        user = None
        
        # Paso 1: Buscar en UserProfile
        try:
            user_profile = UserProfile.objects.get(email=email)
            user = user_profile.user
            print(f"Usuario encontrado en UserProfile: {user.username}")
        except UserProfile.DoesNotExist:
            # Paso 2: Si no está en UserProfile, buscar en User
            try:
                user = User.objects.get(email=email)
                print(f"Usuario encontrado en User: {user.username}")
                
                # Crear perfil si no existe
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'email': user.email}
                )
                if created:
                    print(f"Perfil creado automáticamente para {user.username}")
            except User.DoesNotExist:
                print(f"No se encontró usuario con email: {email}")
                # Por seguridad, no revelar si el email existe
                return render(request, "password_reset_done.html")
        
        # Si llegamos aquí, tenemos un usuario válido
        # Generar token y URL para restablecer contraseña
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')
        
        print(f"URL generada: {reset_url}")
        
        # Enviar email con manejo de errores detallado
        try:
            subject = "Restablecer contraseña - Kakureya"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            
            from_email = settings.EMAIL_HOST_USER
            result = send_mail(
                subject, 
                message, 
                from_email, 
                [email], 
                html_message=message,
                fail_silently=False
            )
            print(f"Resultado del envío: {result}")
            
            return render(request, "password_reset_done.html")
            
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(traceback.format_exc())
            
            messages.error(request, f"Error al enviar el correo: {type(e).__name__}")
            return render(request, "password_reset_form.html")
    
    return render(request, "password_reset_form.html")

def password_reset_confirm(request, uidb64, token):
    try:
        # Decodificar el UID del usuario
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        print(f"Confirmación de restablecimiento para: {user.username}")
        
        # Verificar el token
        if not default_token_generator.check_token(user, token):
            print(f"Token inválido para el usuario: {user.username}")
            return render(request, "password_reset_invalid.html")
        
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                print(f"Contraseña actualizada exitosamente para: {user.username}")
                messages.success(request, "Tu contraseña ha sido actualizada correctamente.")
                return redirect('signin')
            else:
                print(f"Formulario inválido: {form.errors}")
        else:
            form = SetPasswordForm(user)
        
        return render(request, "password_reset_confirm.html", {'form': form})
    
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        print(f"Error en la confirmación de restablecimiento: {e}")
        return render(request, "password_reset_invalid.html")

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone_number')

            # Validaciones personalizadas antes de crear el usuario
            has_errors = False
            if UserProfile.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo ya está registrado.')
                has_errors = True

            if phone and UserProfile.objects.filter(phone_number=phone).exists():
                form.add_error('phone_number', 'Este número de celular ya está registrado.')
                has_errors = True

            if has_errors:
                error_dict = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
                return JsonResponse({'errors': error_dict}, status=400)

            # Crear usuario y perfil desde el formulario (form.save ya incluye UserProfile)
            user = form.save()  # UserRegisterForm se encarga de guardar perfil
            login(request, user)
            return JsonResponse({'success': True, 'redirect': reverse('products')})

        else:
            error_dict = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'errors': error_dict}, status=400)

    return render(request, 'signup.html', {'form': UserRegisterForm()})

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

    return redirect("home")

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        user = None
        
        # Paso 1: Buscar en UserProfile
        try:
            user_profile = UserProfile.objects.get(email=email)
            user = user_profile.user
            print(f"Usuario encontrado en UserProfile: {user.username}")
        except UserProfile.DoesNotExist:
            # Paso 2: Si no está en UserProfile, buscar en User
            try:
                user = User.objects.get(email=email)
                print(f"Usuario encontrado en User: {user.username}")
                
                # Crear perfil si no existe
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'email': user.email}
                )
                if created:
                    print(f"Perfil creado automáticamente para {user.username}")
            except User.DoesNotExist:
                print(f"No se encontró usuario con email: {email}")
                # Por seguridad, no revelar si el email existe
                return render(request, "password_reset_done.html")
        
        # Si llegamos aquí, tenemos un usuario válido
        # Generar token y URL para restablecer contraseña
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')
        
        print(f"URL generada: {reset_url}")
        
        # Enviar email con manejo de errores detallado
        try:
            subject = "Restablecer contraseña - Kakureya"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            
            from_email = settings.EMAIL_HOST_USER
            result = send_mail(
                subject, 
                message, 
                from_email, 
                [email], 
                html_message=message,
                fail_silently=False
            )
            print(f"Resultado del envío: {result}")
            
            return render(request, "password_reset_done.html")
            
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(traceback.format_exc())
            
            messages.error(request, f"Error al enviar el correo: {type(e).__name__}")
            return render(request, "password_reset_form.html")
    
    return render(request, "password_reset_form.html")

def password_reset_confirm(request, uidb64, token):
    try:
        # Decodificar el UID del usuario
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        print(f"Confirmación de restablecimiento para: {user.username}")
        
        # Verificar el token
        if not default_token_generator.check_token(user, token):
            print(f"Token inválido para el usuario: {user.username}")
            return render(request, "password_reset_invalid.html")
        
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                print(f"Contraseña actualizada exitosamente para: {user.username}")
                messages.success(request, "Tu contraseña ha sido actualizada correctamente.")
                return redirect('signin')
            else:
                print(f"Formulario inválido: {form.errors}")
        else:
            form = SetPasswordForm(user)
        
        return render(request, "password_reset_confirm.html", {'form': form})
    
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        print(f"Error en la confirmación de restablecimiento: {e}")
        return render(request, "password_reset_invalid.html")

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
    categoria = request.GET.get('categoria')
    if categoria:
        products = Product.objects.filter(category__iexact=categoria)
    else:
        products = Product.objects.all()
    return render(request, 'products.html', {
        'products': products,
        'categoria_seleccionada': categoria
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
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.user = request.user
            new_product.save()
            return redirect('products')
        else:
            return render(request, 'create_product.html', {
                'form': form,
                'error': 'Existen campos inválidos, por favor verifique.'
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
            categoria = request.POST.get('categoria')
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

    if categoria:
        return redirect(f'/products/?categoria={categoria}')
    else:
        return redirect('products')