from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from kakureya import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('products/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('users/', views.user_management, name='user_management'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:sale_id>/', views.payment, name='payment'),
    path('payment/confirmation/', views.payment_confirmation, name='payment_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('update-order-status/<int:sale_id>/', views.update_order_status, name='update_order_status'),
    path('add_review/', views.add_review, name='add_review'),
    path('moderating_review/', views.review_manager, name='review_manager'),
    path('/edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('/delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('clear-cart/', views.clear_user_cart, name='clear_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)