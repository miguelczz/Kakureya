from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from kakureya import views

urlpatterns = [
    # Panel de administración
    path("admin/", admin.site.urls),

    # Página principal
    path("", views.home, name="home"),

    # Autenticación de usuarios
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),

    # Gestión de usuarios
    path("users/", views.user_management, name="user_management"),

    # Recuperación de contraseña
    path("password-reset/", views.password_reset_request, name="password_reset"),
    path("reset-password/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),

    # Productos
    path("products/", views.products, name="products"),
    path("products/create/", views.create_product, name="create_product"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("products/<int:product_id>/add/", views.add_product, name="add_product"),
    path("products/<int:product_id>/delete/", views.delete_product, name="delete_product"),

    # Carrito de compras
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("clear-cart/", views.clear_user_cart, name="clear_cart"),

    # Checkout y pagos
    path("checkout/", views.checkout, name="checkout"),
    path("payment/<int:sale_id>/", views.payment, name="payment"),
    path("payment/confirmation/", views.payment_confirmation, name="payment_confirmation"),

    # Órdenes
    path("order-history/", views.order_history, name="order_history"),
    path("admin-orders/", views.admin_orders, name="admin_orders"),
    path("update-order-status/<int:sale_id>/", views.update_order_status, name="update_order_status"),

    # Reseñas
    path("add_review/", views.add_review, name="add_review"),
    path("edit_review/<int:review_id>/", views.edit_review, name="edit_review"),
    path("delete_review/<int:review_id>/", views.delete_review, name="delete_review"),
    path("moderating_review/", views.review_manager, name="review_manager"),
]

# Archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
