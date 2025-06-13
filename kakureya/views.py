from .forms import ProductForm, UserRegisterForm, CheckoutForm, ContactForm, ReviewForm
from .models import Sale, SaleItem, UserProfile, CartItem, User, Product, Review
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
import hashlib
import uuid

def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

def home(request):
    submitted = request.GET.get('submitted') == 'true'
    
    reseñas = Review.objects.filter(estado='aprobado')
    for r in reseñas:
        r.full_stars = int(r.calificacion)
        r.has_half = r.calificacion % 1 >= 0.5
        r.empty_stars = 5 - r.full_stars - (1 if r.has_half else 0)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                print("== ENVÍO DE CORREO ==")
                print(f"De: {settings.DEFAULT_FROM_EMAIL}")
                print(f"Para: {settings.DEFAULT_FROM_EMAIL}")
                print(f"Asunto: {cd['subject']}")
                print(f"Mensaje: {cd['message']}")
                
                send_mail(
                    subject=cd['subject'],
                    message=f"Mensaje de {cd['first_name']} {cd['last_name']} ({cd['email']}):\n\n{cd['message']}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                return redirect('/?submitted=true#contact')
            except BadHeaderError:
                print("Fallo por encabezado inválido.")
            except Exception as e:
                print("Error al enviar correo:", e)
        else:
            print("Formulario no válido")
    else:
        form = ContactForm()

    return render(request, 'home.html', {'reseñas': reseñas, 'form': form, 'submitted': submitted})

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

            # Validaciones personalizadas
            errores_personalizados = []

            if UserProfile.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo ya está registrado.')
                errores_personalizados.append('Correo electrónico: Este correo ya está registrado.')

            if phone and UserProfile.objects.filter(phone_number=phone).exists():
                form.add_error('phone_number', 'Este número de celular ya está registrado.')
                errores_personalizados.append('Número de celular: Este número ya está registrado.')

            if errores_personalizados:
                return JsonResponse({'success': False, 'errors': errores_personalizados}, status=400)

            # Crear el usuario y loguearlo
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'redirect': reverse('products')})

        # Errores estándar del formulario
        errores = []
        for campo, lista in form.errors.items():
            for mensaje in lista:
                campo_legible = campo.replace('_', ' ').capitalize()
                errores.append(f"{campo_legible}: {mensaje}")

        return JsonResponse({'success': False, 'errors': errores}, status=400)

    # GET request
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

def generate_wompi_integrity(reference, amount_in_cents, currency="COP"):
    """
    Genera el hash SHA256 para la integridad de Wompi.
    
    Args:
        reference (str): Referencia única de la transacción
        amount_in_cents (int): Monto en centavos (sin puntos ni comas)
        currency (str): Moneda, por defecto COP
        
    Returns:
        str: Hash SHA256 hexadecimal para usar como signature:integrity
    """
    # Obtener el secreto de integridad desde settings
    integrity_secret = settings.WOMPI_INTEGRITY_SECRET
    
    # Concatenar valores en el orden: "<Referencia><Monto><Moneda><SecretoIntegridad>"
    cadena_concatenada = f"{reference}{amount_in_cents}{currency}{integrity_secret}"
    
    # Generar el hash SHA256 siguiendo el ejemplo de Wompi
    m = hashlib.sha256()
    m.update(bytes(cadena_concatenada, 'utf-8'))
    
    # Devolver como representación hexadecimal
    return m.hexdigest()

@login_required
def checkout(request):
    # Obtener items del carrito
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    if not cart_items:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('products')
    
    # Calcular totales
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_cost = Decimal('5000')  # Costo fijo de envío
    total = subtotal + shipping_cost
    
    # Obtener dirección del usuario si existe
    try:
        profile = UserProfile.objects.get(user=request.user)
        initial_data = {
            'address': profile.address or '',
            'phone': profile.phone_number or '',
        }
    except UserProfile.DoesNotExist:
        initial_data = {}
    
    form = CheckoutForm(request.POST or None, initial=initial_data)
    
    if request.method == 'POST' and form.is_valid():
        # Crear la venta pendiente
        # Generar referencia única para Wompi
        reference = f"KK-{request.user.id}-{int(timezone.now().timestamp())}-{uuid.uuid4().hex[:8]}"
        
        sale = Sale(
            user=request.user,
            status='preparing',
            address=form.cleaned_data['address'],
            notes=form.cleaned_data.get('notes', ''),
            payment_reference=reference,
            is_paid=False
        )
        sale.save()
        
        # Transferir items desde el carrito a la venta
        for item in cart_items:
            SaleItem.objects.create(
                sale=sale,
                product=item.product,
                quantity=item.quantity,
                price_at_sale=item.product.price
            )
        
        # Guardar dirección del usuario si se seleccionó esa opción
        if form.cleaned_data.get('save_address'):
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'email': request.user.email}
            )
            profile.address = form.cleaned_data['address']
            profile.phone_number = form.cleaned_data['phone']
            profile.save()
        
        # Redireccionar a la vista de pago
        return redirect('payment', sale_id=sale.id)
    
    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total
    })

@login_required
def payment(request, sale_id):
    # Obtener la venta
    sale = get_object_or_404(Sale, id=sale_id, user=request.user)
    
    # Verificar que la venta no haya sido pagada
    if sale.is_paid:
        messages.info(request, 'Esta venta ya ha sido pagada')
        return redirect('order_history')
    
    # Calcular el total de la venta en centavos para Wompi
    sale_items = SaleItem.objects.filter(sale=sale)
    subtotal = sum(item.quantity * item.price_at_sale for item in sale_items)
    shipping_cost = Decimal('5000')
    total = subtotal + shipping_cost
    amount_in_cents = int(total * 100)  # Convertir a centavos
    
    # Generar el hash de integridad para Wompi
    integrity_hash = generate_wompi_integrity(
        reference=sale.payment_reference,
        amount_in_cents=amount_in_cents,
        currency="COP"
    )
    
    # Preparar datos para el widget de Wompi
    wompi_data = {
        'reference': sale.payment_reference,
        'amount_in_cents': amount_in_cents,
        'integrity_hash': integrity_hash,
        'public_key': settings.WOMPI_PUBLIC_KEY
    }
    
    return render(request, 'payment.html', {
        'sale': sale,
        'sale_items': sale_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
        'wompi_data': wompi_data
    })

@login_required
def payment_confirmation(request):
    """Vista para manejar la redirección después del pago con Wompi"""
    # Obtener parámetros de la URL enviados por Wompi
    reference = request.GET.get('reference')
    transaction_id = request.GET.get('id')
    status = request.GET.get('status')
    
    if not reference:
        messages.error(request, "Error en la transacción: No se recibió la referencia")
        return redirect('products')
    
    try:
        # Buscar la venta correspondiente por la referencia
        sale = Sale.objects.get(payment_reference=reference)
        
        # Verificar que el usuario actual sea el propietario de la venta o un administrador
        if request.user != sale.user and not is_admin(request.user):
            messages.warning(request, "No tienes permisos para ver esta venta")
            return redirect('products')
            
        # Procesar según el estado de la transacción
        if status == 'APPROVED':
            # CAMBIO PRINCIPAL: Siempre vaciar el carrito si el pago fue aprobado
            CartItem.objects.filter(user=request.user).delete()
            
            # MODIFICACIÓN PARA PRUEBAS: En entorno de pruebas, siempre marcar como pagado
            # Detectar si estamos en entorno de pruebas basado en la clave pública de Wompi
            is_test_environment = settings.WOMPI_PUBLIC_KEY.startswith('pub_test_')
            
            # Si es un entorno de pruebas o si el pago no está marcado como pagado aún
            if is_test_environment or not sale.is_paid:
                sale.is_paid = True
                sale.payment_id = transaction_id or f'test_{int(timezone.now().timestamp())}'
                sale.payment_method = 'wompi'
                sale.save()
                
                # Actualizar inventario
                for item in sale.items.all():
                    product = item.product
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                        product.save()
                
                # Mostrar mensaje específico para entorno de pruebas
                if is_test_environment:
                    messages.info(request, "Pago simulado en entorno de pruebas. Pedido marcado como pagado.")
            
            messages.success(request, "¡Pago exitoso! Tu pedido está siendo preparado.")
            return render(request, 'payment_success.html', {'sale': sale})
            
        elif status == 'DECLINED':
            messages.error(request, "El pago fue rechazado por la entidad financiera.")
            return render(request, 'payment_failed.html', {'sale': sale, 'status': status})
            
        elif status == 'VOIDED':
            messages.error(request, "El pago fue anulado.")
            return render(request, 'payment_failed.html', {'sale': sale, 'status': status})
            
        else:  # PENDING u otros estados
            messages.warning(request, f"El pago está en estado: {status}. Te notificaremos cuando se complete.")
            return render(request, 'payment_pending.html', {'sale': sale, 'status': status})
            
    except Sale.DoesNotExist:
        messages.error(request, "Error: No se encontró la venta correspondiente")
        return redirect('products')

@login_required
def order_history(request):
    """Vista para mostrar el historial de pedidos del usuario"""
    sales = Sale.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'sales': sales})

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
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product').order_by('added_at')
    
    # Calcular subtotal para cada item y el total del carrito
    total = 0
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def remove_from_cart(request, item_id): #Para eliminar un producto del carrito
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        cart_item.delete()
        messages.success(request, 'Producto eliminado del carrito')
    return redirect('cart')

@require_POST
@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get("action")
    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1
    item.save()

    new_subtotal = item.product.price * item.quantity
    total = sum(i.product.price * i.quantity for i in CartItem.objects.filter(user=request.user))

    return JsonResponse({
        "new_quantity": item.quantity,
        "new_subtotal": f"{new_subtotal:.0f}",
        "new_total": f"{total:.0f}",
    })

@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    """Vista para que los administradores gestionen los pedidos"""
    filter_status = request.GET.get('filter', 'all')
    
    if filter_status == 'all':
        sales = Sale.objects.all().order_by('-created_at')
    else:
        sales = Sale.objects.filter(status=filter_status).order_by('-created_at')
    
    return render(request, 'admin_orders.html', {
        'sales': sales,
        'filter': filter_status
    })

# Modificar la función update_order_status

@login_required
@user_passes_test(is_admin)
def update_order_status(request, sale_id):
    """Vista para actualizar el estado de un pedido y/o su estado de pago"""
    if request.method == 'POST':
        sale = get_object_or_404(Sale, id=sale_id)
        old_status = sale.status
        new_status = request.POST.get('status')
        
        # Actualizar estado del pedido
        if new_status in dict(Sale.STATUS_CHOICES).keys() and old_status != new_status:
            sale.status = new_status
            is_status_updated = True
        else:
            is_status_updated = False
        
        # Actualizar estado de pago
        payment_status = request.POST.get('payment_status')
        if payment_status in ['paid', 'unpaid']:
            old_payment_status = sale.is_paid
            new_payment_status = (payment_status == 'paid')
            
            if old_payment_status != new_payment_status:
                sale.is_paid = new_payment_status
                
                # Si se marca como pagado, establecer un ID de pago simulado
                if new_payment_status:
                    if not sale.payment_id:
                        sale.payment_id = f'admin_{int(timezone.now().timestamp())}'
                    if not sale.payment_method:
                        sale.payment_method = 'manual'
                
                is_payment_updated = True
            else:
                is_payment_updated = False
        else:
            is_payment_updated = False
        
        # Guardar cambios si hubo alguna actualización
        if is_status_updated or is_payment_updated:
            sale.save()
            
            # Notificaciones para cada tipo de cambio
            updates = []
            if is_status_updated:
                updates.append(f"estado a '{sale.get_status_display()}'")
            if is_payment_updated:
                updates.append(f"estado de pago a '{'Pagado' if sale.is_paid else 'No pagado'}'")
            
            messages.success(request, f"Pedido #{sale.id} actualizado: {' y '.join(updates)}")
            
            # Enviar notificación por email al cliente
            try:
                subject = f"Actualización de tu pedido #{sale.id} en Kakureya"
                message = render_to_string('email/order_status_update.html', {
                    'sale': sale,
                    'user': sale.user,
                    'status': sale.get_status_display(),
                    'payment_updated': is_payment_updated,
                })
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [sale.user.email],
                    html_message=message,
                    fail_silently=True
                )
            except Exception as e:
                messages.warning(request, f"No se pudo enviar la notificación por email: {str(e)}")
        
    return redirect('admin_orders')

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
            form = ProductForm(request.POST, request.FILES, instance=product)
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

        action = request.POST.get('action')
        categoria = request.POST.get('categoria')

        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

        # PRIORIDAD 1: Ir a pagar
        if action == 'add_and_pay':
            return redirect('cart')  # Tu URL de carrito
        
        # PRIORIDAD 2: Mantener categoría si existe
        if categoria:
            return redirect(f'/products/?categoria={categoria}')
        
        # PRIORIDAD 3: Si no, ir a productos
        return redirect('products')
    
    # Fallback en caso de error
    return redirect('products')

@login_required
def clear_user_cart(request):
    """Vista para que el usuario pueda vaciar su propio carrito manualmente"""
    if request.method == 'POST':
        # Vaciar el carrito del usuario actual
        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, "Tu carrito ha sido vaciado")
        
        # Redireccionar a la página especificada o por defecto a productos
        if 'next' in request.POST:
            return redirect(request.POST.get('next'))
        return redirect('products')
    
    # Si no es POST, redirigir
    return redirect('products')

@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            reseña = form.save(commit=False)
            reseña.nombre = request.user.get_full_name() or request.user.username
            reseña.usuario = request.user
            reseña.save()
            return render(request, 'review_process.html')
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, usuario=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.usuario = request.user
            updated_review.nombre = request.user.first_name or request.user.username
            updated_review.estado = 'pendiente'
            updated_review.save()
            return redirect(request, 'review_process.html')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'edit_review.html', {
        'form': form,
        'review': review,
    })

@login_required
@user_passes_test(is_admin)
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, "La reseña fue eliminada correctamente.")
        return redirect('/#reviews')

    return render(request, 'confirm_delete.html', {'review': review})

@staff_member_required
def review_manager(request):
    reseñas = Review.objects.filter(estado='pendiente')
    if request.method == 'POST':
        id = request.POST.get('id')
        decision = request.POST.get('accion')
        reseña = Review.objects.get(id=id)
        reseña.estado = decision
        reseña.save()
    return render(request, 'moderating_review.html', {'reseñas': reseñas})