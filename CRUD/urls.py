"""
URL configuration for CRUD project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from kakureya import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('products/', views.products, name='products'),
    path('products_added/', views.products_added, name='products_added'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/<int:product_id>/quit/', views.quit_product, name='quit_product'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
]
