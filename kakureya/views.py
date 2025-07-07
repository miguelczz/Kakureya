"""
Vistas principales de la aplicación. Se agrupan por tipo: utilidades,
autenticación, tienda, carrito y ventas. Cada bloque incluye comentarios
que describen el propósito de la vista.
"""

# --- Librerías estándar -------------------------------------------------
import uuid
import hashlib
from decimal import Decimal

# --- Django core --------------------------------------------------------
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail, BadHeaderError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST

# --- Modelos y formularios del proyecto --------------------------------
from .models import (
    Product,
    CartItem,
    Sale,
    SaleItem,
    UserProfile,
    Review,
)
from .forms import (
    ProductForm,
    UserRegisterForm,
    CheckoutForm,
    ContactForm,
    ReviewForm,
)

# -----------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------

def is_admin(user):
    """Devuelve True si el usuario pertenece al grupo 'Administrador'."""
    return user.groups.filter(name="Administrador").exists()


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

# -----------------------------------------------------------------------
# Vistas públicas
# -----------------------------------------------------------------------

def home(request):
    """
    Página principal. Muestra las reseñas aprobadas y procesa el
    formulario de contacto.
    """
    # Detecta si se acaba de enviar el formulario de contacto
    submitted = request.GET.get("submitted") == "true"

    # Obtiene reseñas aprobadas y prepara las estrellas para la plantilla
    reseñas = Review.objects.filter(estado="aprobado")
    for r in reseñas:
        r.full_stars = int(r.calificacion)
        r.has_half = r.calificacion % 1 >= 0.5
        r.empty_stars = 5 - r.full_stars - (1 if r.has_half else 0)

    # Procesa el formulario de contacto
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                # Envío de correo (se imprime en consola en lugar de enviar)
                print("== ENVÍO DE CORREO ==")
                print(f"De: {settings.DEFAULT_FROM_EMAIL}")
                print(f"Para: {settings.DEFAULT_FROM_EMAIL}")
                print(f"Asunto: {cd['subject']}")
                print(f"Mensaje: {cd['message']}")

                send_mail(
                    subject=cd["subject"],
                    message=(
                        f"Mensaje de {cd['first_name']} {cd['last_name']} "
                        f"({cd['email']}):\n\n{cd['message']}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                # Redirige con parámetro de éxito
                return redirect("/?submitted=true#contact")
            except BadHeaderError:
                print("Fallo por encabezado inválido.")
            except Exception as e:
                print("Error al enviar correo:", e)
        else:
            print("Formulario de contacto no válido")
    else:
        form = ContactForm()

    contexto = {
        "reseñas": reseñas,
        "form": form,
        "submitted": submitted,
    }
    return render(request, "home.html", contexto)

# -----------------------------------------------------------------------
# Vistas de autenticación
# -----------------------------------------------------------------------

def signup(request):
    """
    Vista de registro de usuarios. Valida correo y número antes de crear el usuario.
    Responde con JSON si hay errores personalizados o éxito.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone_number')

            # Validaciones de unicidad en el perfil
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

        # Recolectar errores estándar del formulario
        errores = []
        for campo, lista in form.errors.items():
            for mensaje in lista:
                campo_legible = campo.replace('_', ' ').capitalize()
                errores.append(f"{campo_legible}: {mensaje}")

        return JsonResponse({'success': False, 'errors': errores}, status=400)

    # Renderiza formulario en GET
    return render(request, 'signup.html', {'form': UserRegisterForm()})


def signin(request):
    """
    Vista de inicio de sesión. Autentica al usuario a partir del correo y contraseña.
    """
    if request.method == "GET":
        return render(request, "signin.html")

    email = request.POST.get("email")
    password = request.POST.get("password")

    # Buscar usuario por email
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return render(request, "signin.html", {
            "error": "Correo o contraseña incorrectos"
        })

    # Autenticar usando username del usuario
    user = authenticate(request, username=user_obj.username, password=password)
    if user is None:
        return render(request, "signin.html", {
            "error": "Correo o contraseña incorrectos"
        })

    login(request, user)
    return redirect("home")


@login_required
def signout(request):
    """
    Cierra la sesión del usuario autenticado.
    """
    logout(request)
    return redirect('home')


# -----------------------------------------------------------------------
# Vistas de restablecimiento de contraseña
# -----------------------------------------------------------------------

def password_reset_request(request):
    """
    Solicitud de restablecimiento de contraseña.
    Busca al usuario por email, genera token y envía URL al correo.
    """
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        user = None

        # Buscar en perfil personalizado
        try:
            user_profile = UserProfile.objects.get(email=email)
            user = user_profile.user
            print(f"Usuario encontrado en UserProfile: {user.username}")
        except UserProfile.DoesNotExist:
            # Buscar directamente en User
            try:
                user = User.objects.get(email=email)
                print(f"Usuario encontrado en User: {user.username}")
                # Crear perfil si no existía
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'email': user.email}
                )
                if created:
                    print(f"Perfil creado automáticamente para {user.username}")
            except User.DoesNotExist:
                print(f"No se encontró usuario con email: {email}")
                # Mostrar pantalla de éxito genérica para evitar fugas de información
                return render(request, "password_reset_done.html")

        # Generar token y URL personalizada
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')
        print(f"URL generada: {reset_url}")

        # Enviar correo con el enlace de restablecimiento
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
            import traceback
            print(traceback.format_exc())
            messages.error(request, f"Error al enviar el correo: {type(e).__name__}")
            return render(request, "password_reset_form.html")

    return render(request, "password_reset_form.html")


def password_reset_confirm(request, uidb64, token):
    """
    Confirma el token y permite al usuario definir nueva contraseña.
    """
    try:
        # Decodificar el identificador
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(f"Confirmación de restablecimiento para: {user.username}")

        # Verificar que el token sea válido
        if not default_token_generator.check_token(user, token):
            print(f"Token inválido para el usuario: {user.username}")
            return render(request, "password_reset_invalid.html")

        # Si el método es POST, validar y guardar nueva contraseña
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

# -----------------------------------------------------------------------
# Gestión de usuarios (solo administradores)
# -----------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def user_management(request):
    """
    Vista administrativa para gestionar usuarios del sistema.
    
    Permite:
    - Listar todos los usuarios (excepto el que está autenticado).
    - Eliminar usuarios seleccionados.
    - Asignar un grupo (rol) a cada usuario.

    Requiere que el usuario tenga permisos de administrador. Se accede 
    usualmente desde el panel de control de gestión interna.
    """
    # Excluir al usuario autenticado de la lista
    users = User.objects.exclude(username=request.user.username)
    
    # Obtener todos los grupos
    grupos = Group.objects.all()

    # Procesamiento del formulario
    if request.method == 'POST':
        # Eliminación de usuario
        if 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            user.delete()
            return redirect('user_management')

        # Asignación de grupo a usuario
        elif 'assign_group' in request.POST:
            user_id = request.POST.get('user_id')
            group_id = request.POST.get('group_id')
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            user.groups.clear()
            user.groups.add(group)
            return redirect('user_management')

    # Renderiza la interfaz con la lista de usuarios y grupos
    return render(request, 'user_management.html', {
        'users': users,
        'grupos': grupos
    })
    
# -----------------------------------------------------------------------
# Productos
# -----------------------------------------------------------------------

def products(request):
    """
    Vista pública que muestra todos los productos disponibles en la tienda.
    Permite aplicar un filtro por categoría si se recibe en la URL.
    """
    # Leer la categoría desde el parámetro GET
    categoria = request.GET.get('categoria')

    # Filtra por categoría si se especifica, o muestra todos los productos
    if categoria:
        products = Product.objects.filter(category__iexact=categoria)
    else:
        products = Product.objects.all()

    return render(request, 'products.html', {
        'products': products,
        'categoria_seleccionada': categoria
    })


@login_required
def create_product(request):
    """
    Vista protegida para que un usuario autenticado cree un nuevo producto.
    Muestra el formulario en GET y procesa la creación en POST.
    """
    if request.method == 'GET':
        # Mostrar formulario vacío de creación
        return render(request, 'create_product.html', {
            'form': ProductForm()
        })

    elif request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        # Validación del formulario
        if form.is_valid():
            # Asociar el producto al usuario actual antes de guardar
            new_product = form.save(commit=False)
            new_product.user = request.user
            new_product.save()
            # Redirige a la lista de productos tras guardar
            return redirect('products')
        else:
            # Si el formulario es inválido, volver a mostrar con errores
            return render(request, 'create_product.html', {
                'form': form,
                'error': 'Existen campos inválidos, por favor verifique.'
            })


@login_required
def product_detail(request, product_id):
    """
    Vista para mostrar o editar los detalles de un producto específico.
    GET muestra el formulario precargado, POST actualiza el producto.
    """
    # Buscar el producto por ID, o lanzar 404 si no existe
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'GET':
        # Mostrar el formulario con datos del producto actual
        form = ProductForm(instance=product)
        return render(request, 'product_detail.html', {
            'product': product,
            'form': form
        })

    else:
        try:
            # Procesar los cambios enviados por POST
            form = ProductForm(request.POST, request.FILES, instance=product)
            form.save()
            # Redirige si la edición fue exitosa
            return redirect('products')
        except ValueError:
            # En caso de error, volver a mostrar el formulario con mensaje
            return render(request, 'product_detail.html', {
                'product': product,
                'form': form,
                'error': 'Campos inválidos'
            })


@login_required
def add_product(request, product_id):
    """
    Marca un producto como recientemente agregado actualizando la fecha `added`.
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Actualiza la fecha de adición
        product.added = timezone.now()
        product.save()
        return redirect('products')

    # Mostrar confirmación previa (si aplica)
    return render(request, 'add_product.html', {'product': product})


@login_required
def delete_product(request, product_id):
    """
    Vista protegida para eliminar un producto específico.
    Solo responde a solicitudes POST para evitar eliminaciones accidentales.
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Elimina el producto de la base de datos
        product.delete()
        return redirect('products')

# -----------------------------------------------------------------------
# Carrito de compras
# -----------------------------------------------------------------------

@login_required
def add_to_cart(request, product_id):
    """
    Agrega un producto al carrito del usuario autenticado.
    
    Si ya existe, incrementa la cantidad. Adicionalmente:
    - Si se recibe 'add_and_pay' como acción, redirige al carrito.
    - Si se recibe una categoría, vuelve a esa vista filtrada.
    - En otros casos, redirige a la lista general de productos.
    """
    # Obtener el producto solicitado o lanzar 404 si no existe
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Obtener la cantidad del formulario; manejar errores
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        # Leer opciones adicionales del formulario
        action = request.POST.get('action')
        categoria = request.POST.get('categoria')

        # Buscar o crear item en el carrito
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            cart_item.quantity = quantity  # Nueva entrada
        else:
            cart_item.quantity += quantity  # Ya existe, incrementar
        cart_item.save()

        # Redireccionar según prioridades
        if action == 'add_and_pay':
            return redirect('cart')  # Ir al carrito directamente

        if categoria:
            return redirect(f'/products/?categoria={categoria}')  # Mantener contexto

        return redirect('products')  # Fallback a productos

    # Si el método no es POST, redirige por seguridad
    return redirect('products')


@login_required
def clear_user_cart(request):
    """
    Permite al usuario vaciar manualmente su carrito de compras.
    Sólo responde a POST para evitar vaciados accidentales.
    """
    if request.method == 'POST':
        # Elimina todos los ítems del carrito del usuario actual
        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, "Tu carrito ha sido vaciado")

        # Redirige a la URL especificada o, si no hay, a productos
        if 'next' in request.POST:
            return redirect(request.POST.get('next'))
        return redirect('products')

    return redirect('products')  # Rechaza GET por seguridad


@require_POST
@login_required
def update_cart_quantity(request, item_id):
    """
    Actualiza la cantidad de un ítem en el carrito.
    Permite aumentar o disminuir desde botones de cantidad.
    """
    # Obtener el ítem del carrito o lanzar 404 si no es válido
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    action = request.POST.get("action")

    # Actualiza la cantidad según la acción recibida
    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

    item.save()

    # Calcular subtotales y total para respuesta en tiempo real (AJAX)
    new_subtotal = item.product.price * item.quantity
    total = sum(
        i.product.price * i.quantity
        for i in CartItem.objects.filter(user=request.user)
    )

    return JsonResponse({
        "new_quantity": item.quantity,
        "new_subtotal": f"{new_subtotal:.0f}",
        "new_total": f"{total:.0f}",
    })


@login_required
def cart(request):
    """
    Muestra el contenido actual del carrito de compras.
    Calcula subtotales por ítem y el total acumulado.
    """
    # Obtener ítems del carrito con datos del producto
    cart_items = CartItem.objects.filter(user=request.user)\
                                 .select_related('product')\
                                 .order_by('added_at')

    # Calcular subtotal por ítem y total general
    total = 0
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def remove_from_cart(request, item_id):
    """
    Elimina un producto específico del carrito del usuario.
    Sólo responde a POST por seguridad.
    """
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if request.method == 'POST':
        cart_item.delete()
        messages.success(request, 'Producto eliminado del carrito')

    return redirect('cart')

# -----------------------------------------------------------------------
# Proceso de compra y pago
# -----------------------------------------------------------------------

@login_required
def checkout(request):
    """
    Vista que inicia el proceso de compra.  
    - Verifica que el carrito no esté vacío.  
    - Calcula subtotal, envío y total.  
    - Crea una venta en estado preparing y transfiere los ítems del carrito
      a SaleItem.  
    - Redirige a la vista payment para completar el pago.
    """
    # 1️ Obtener ítems del carrito del usuario
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    if not cart_items:
        messages.warning(request, "Tu carrito está vacío")
        return redirect("products")

    # 2️ Calcular totales
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_cost = Decimal("5000")   # Costo fijo de envío (COP)
    total = subtotal + shipping_cost

    # 3️ Pre-cargar dirección y teléfono si el usuario ya los tiene guardados
    try:
        profile = UserProfile.objects.get(user=request.user)
        initial_data = {
            "address": profile.address or "",
            "phone": profile.phone_number or "",
        }
    except UserProfile.DoesNotExist:
        initial_data = {}

    form = CheckoutForm(request.POST or None, initial=initial_data)

    # 4️ Procesar envío del formulario
    if request.method == "POST" and form.is_valid():
        # Generar referencia única para Wompi: KK-<userID>-<timestamp>-<8 hex>
        reference = (
            f"KK-{request.user.id}-{int(timezone.now().timestamp())}-"
            f"{uuid.uuid4().hex[:8]}"
        )

        # Crear la venta pendiente
        sale = Sale.objects.create(
            user=request.user,
            status="preparing",
            address=form.cleaned_data["address"],
            notes=form.cleaned_data.get("notes", ""),
            payment_reference=reference,
            is_paid=False,
        )

        # Transferir ítems del carrito a SaleItem
        for item in cart_items:
            SaleItem.objects.create(
                sale=sale,
                product=item.product,
                quantity=item.quantity,
                price_at_sale=item.product.price,
            )

        # Guardar dirección en perfil si el usuario lo solicita
        if form.cleaned_data.get("save_address"):
            profile, _ = UserProfile.objects.get_or_create(
                user=request.user, defaults={"email": request.user.email}
            )
            profile.address = form.cleaned_data["address"]
            profile.phone_number = form.cleaned_data["phone"]
            profile.save()

        return redirect("payment", sale_id=sale.id)

    # 5️ Renderizar plantilla de checkout
    return render(
        request,
        "checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "total": total,
        },
    )


@login_required
def payment(request, sale_id):
    """
    Renderiza la página de pago con el widget de Wompi.  
    - Verifica que la venta pertenezca al usuario y no esté pagada.  
    - Calcula el monto en centavos y genera el *integrity hash* requerido 
      por Wompi.  
    - Envía los datos a la plantilla para inicializar el widget.
    """
    # Obtener la venta o responder 404 si no existe
    sale = get_object_or_404(Sale, id=sale_id, user=request.user)

    # Evitar pagos duplicados
    if sale.is_paid:
        messages.info(request, "Esta venta ya ha sido pagada")
        return redirect("order_history")

    # Calcular totales nuevamente (seguridad)
    sale_items = SaleItem.objects.filter(sale=sale)
    subtotal = sum(i.quantity * i.price_at_sale for i in sale_items)
    shipping_cost = Decimal("5000")
    total = subtotal + shipping_cost
    amount_in_cents = int(total * 100)  # Wompi usa centavos

    # Generar hash de integridad SHA-256 (ref + amount + currency + secret)
    integrity_hash = generate_wompi_integrity(
        reference=sale.payment_reference,
        amount_in_cents=amount_in_cents,
        currency="COP",
    )

    # Datos que requiere el widget de Wompi
    wompi_data = {
        "reference": sale.payment_reference,
        "amount_in_cents": amount_in_cents,
        "integrity_hash": integrity_hash,
        "public_key": settings.WOMPI_PUBLIC_KEY,
    }

    return render(
        request,
        "payment.html",
        {
            "sale": sale,
            "sale_items": sale_items,
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "total": total,
            "wompi_data": wompi_data,
        },
    )


@login_required
def payment_confirmation(request):
    """
    Procesa la redirección de Wompi después del intento de pago.  
    - Valida referencia y estado (APPROVED, DECLINED, VOIDED, PENDING).  
    - Si es APPROVED, vacía el carrito, marca la venta como pagada y
      actualiza inventario.  
    - Muestra la plantilla correspondiente según el resultado.
    """
    # Extraer parámetros devueltos por Wompi
    reference = request.GET.get("reference")
    transaction_id = request.GET.get("id")
    status = request.GET.get("status")

    if not reference:
        messages.error(request, "Error en la transacción: Falta la referencia")
        return redirect("products")

    try:
        sale = Sale.objects.get(payment_reference=reference)
    except Sale.DoesNotExist:
        messages.error(request, "Error: No se encontró la venta correspondiente")
        return redirect("products")

    # Control de acceso: dueño de la venta o admin
    if request.user != sale.user and not is_admin(request.user):
        messages.warning(request, "No tienes permisos para ver esta venta")
        return redirect("products")

    # ---- Procesar estado devuelto por Wompi -----------------------------
    if status == "APPROVED":
        # 1 Vaciar el carrito si el pago fue exitoso
        CartItem.objects.filter(user=request.user).delete()

        # 2 Entorno de prueba: marcar pagado
        is_test_environment = settings.WOMPI_PUBLIC_KEY.startswith("pub_test_")

        if is_test_environment or not sale.is_paid:
            sale.is_paid = True
            sale.payment_id = transaction_id or f"test_{int(timezone.now().timestamp())}"
            sale.payment_method = "wompi"
            sale.save()

            # 3 Reducir inventario
            for item in sale.items.all():
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()

            if is_test_environment:
                messages.info(
                    request,
                    "Pago simulado en entorno de pruebas. Pedido marcado como pagado.",
                )

        messages.success(request, "¡Pago exitoso! Tu pedido está siendo preparado.")
        return render(request, "payment_success.html", {"sale": sale})

    elif status == "DECLINED":
        messages.error(request, "El pago fue rechazado por la entidad financiera.")
        return render(request, "payment_failed.html", {"sale": sale, "status": status})

    elif status == "VOIDED":
        messages.error(request, "El pago fue anulado.")
        return render(request, "payment_failed.html", {"sale": sale, "status": status})

    else:  # PENDING u otros estados
        messages.warning(
            request,
            f"El pago está en estado: {status}. Te notificaremos cuando se complete.",
        )
        return render(request, "payment_pending.html", {"sale": sale, "status": status})


@login_required
def order_history(request):
    """
    Muestra el historial de pedidos del usuario autenticado,
    ordenado del más reciente al más antiguo.
    """
    sales = Sale.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "order_history.html", {"sales": sales})

# -----------------------------------------------------------------------
# Gestión administrativa de pedidos (solo administradores)
# -----------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    """
    Panel de administración para visualizar y filtrar pedidos.

    Permite al personal con rol de *Administrador*:
    1. Ver la lista completa de ventas.
    2. Aplicar un filtro por estado mediante el parámetro GET `filter`
       (p. ej. `?filter=shipped`).  
    3. Ordenar los pedidos del más reciente al más antiguo.
    """
    # Leer criterio de filtro; por defecto, 'all'
    filter_status = request.GET.get("filter", "all")

    # Consultar ventas según el estado solicitado
    if filter_status == "all":
        sales = Sale.objects.all().order_by("-created_at")
    else:
        sales = Sale.objects.filter(status=filter_status).order_by("-created_at")

    return render(
        request,
        "admin_orders.html",
        {
            "sales": sales,
            "filter": filter_status,
        },
    )


@login_required
@user_passes_test(is_admin)
def update_order_status(request, sale_id):
    """
    Actualiza el estado logístico (status) y/o el estado de pago
    (is_paid) de un pedido.

    Flujo en POST:
    1. Valida que el nuevo estado existe y difiere del actual.  
    2. Permite marcar el pedido como pagado/no pagado.  
    3. Registra un (payment_id) simulado si el admin marca como pagado.  
    4. Envía una notificación al cliente y muestra un mensaje de éxito.  
    """
    if request.method == "POST":
        sale = get_object_or_404(Sale, id=sale_id)

        # 1. Actualizar estado logístico
        old_status = sale.status
        new_status = request.POST.get("status")
        is_status_updated = (
            new_status in dict(Sale.STATUS_CHOICES).keys() and old_status != new_status
        )
        if is_status_updated:
            sale.status = new_status

        # 2. Actualizar estado de pago
        payment_status = request.POST.get("payment_status")  # 'paid' o 'unpaid'
        is_payment_updated = False

        if payment_status in ["paid", "unpaid"]:
            old_paid = sale.is_paid
            new_paid = payment_status == "paid"

            if old_paid != new_paid:
                sale.is_paid = new_paid
                is_payment_updated = True

                # Generar datos de pago simulados si el admin marca como pagado
                if new_paid:
                    if not sale.payment_id:
                        sale.payment_id = f"admin_{int(timezone.now().timestamp())}"
                    if not sale.payment_method:
                        sale.payment_method = "manual"

        # 3. Guardar y notificar si hubo cambios
        if is_status_updated or is_payment_updated:
            sale.save()

            # Componer mensaje para el administrador
            updates = []
            if is_status_updated:
                updates.append(f"estado a «{sale.get_status_display()}»")
            if is_payment_updated:
                updates.append(
                    f"estado de pago a «{'Pagado' if sale.is_paid else 'No pagado'}»"
                )
            messages.success(request, f"Pedido #{sale.id} actualizado: {' y '.join(updates)}")

            # Enviar correo al cliente
            try:
                subject = f"Actualización de tu pedido #{sale.id} en Kakureya"
                message = render_to_string(
                    "email/order_status_update.html",
                    {
                        "sale": sale,
                        "user": sale.user,
                        "status": sale.get_status_display(),
                        "payment_updated": is_payment_updated,
                    },
                )
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [sale.user.email],
                    html_message=message,
                    fail_silently=True,
                )
            except Exception as e:
                messages.warning(
                    request, f"No se pudo enviar la notificación por email: {str(e)}"
                )

    # Redirigir siempre al panel de administración de pedidos
    return redirect("admin_orders")

# -----------------------------------------------------------------------
# Reseñas de usuarios
# -----------------------------------------------------------------------

@login_required
def add_review(request):
    """
    Permite al usuario autenticado crear una reseña.  
    Flujo:  
    1. Muestra el formulario `ReviewForm` en GET.  
    2. Valida y guarda la reseña en POST, asociándola al usuario.  
    3. Redirige a una plantilla de confirmación de envío.
    """
    if request.method == "POST":
        form = ReviewForm(request.POST)

        # Validar formulario
        if form.is_valid():
            reseña = form.save(commit=False)
            reseña.nombre = request.user.get_full_name() or request.user.username
            reseña.usuario = request.user
            reseña.save()
            return render(request, "review_process.html")
    else:
        form = ReviewForm()  # Formulario vacío

    return render(request, "add_review.html", {"form": form})


@login_required
def edit_review(request, review_id):
    """
    Permite al usuario editar su propia reseña.  
    - Carga la reseña (404 si no le pertenece).  
    - En GET muestra el formulario precargado.  
    - En POST valida y guarda los cambios, marcando la reseña nuevamente
      como *pendiente* para re-aprobación por un moderador.
    """
    review = get_object_or_404(Review, id=review_id, usuario=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)

        # Validar y guardar cambios
        if form.is_valid():
            updated = form.save(commit=False)
            updated.usuario = request.user
            updated.nombre = request.user.first_name or request.user.username
            updated.estado = "pendiente"  # Requiere nueva aprobación
            updated.save()
            return render(request, "review_process.html")
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "edit_review.html",
        {
            "form": form,
            "review": review,
        },
    )


@login_required
@user_passes_test(is_admin)
def delete_review(request, review_id):
    """
    Elimina una reseña (solo administradores).  
    Responde solo a POST para prevenir borrados accidentales.
    """
    review = get_object_or_404(Review, id=review_id)

    if request.method == "POST":
        review.delete()
        messages.success(request, "La reseña fue eliminada correctamente.")
        return redirect("/#reviews")

    return render(request, "confirm_delete.html", {"review": review})


@staff_member_required
def review_manager(request):
    """
    Panel de moderación para personal *staff*.  
    - Lista reseñas en estado *pendiente*.  
    - Permite aprobar (accion=aprobado) o rechazar (accion=rechazado)
      una reseña mediante POST.
    """
    reseñas = Review.objects.filter(estado="pendiente")

    if request.method == "POST":
        review_id = request.POST.get("id")
        decision = request.POST.get("accion")  # 'aprobado' | 'rechazado'
        reseña = get_object_or_404(Review, id=review_id)
        reseña.estado = decision
        reseña.save()

    return render(request, "moderating_review.html", {"reseñas": reseñas})
