# Formularios personalizados para productos, usuarios, reseñas, contacto y checkout

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Review, UserProfile

# --- Formulario de producto ---
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del producto'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Precio del producto'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

# --- Formulario de registro de usuario ---
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer nombre'}))
    middle_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo nombre (opcional)'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer apellido'}))
    second_last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo apellido'}))
    dni = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Documento de identidad'}))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Dirección completa', 'rows': 3}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono (opcional)'}))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'middle_name', 'last_name', 'second_last_name', 
                  'dni', 'address', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        email_username = self.cleaned_data['email'].split('@')[0]
        base_username = email_username
        counter = 1
        while User.objects.filter(username=email_username).exists():
            email_username = f"{base_username}{counter}"
            counter += 1
        user.username = email_username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'email': self.cleaned_data['email'],
                    'first_name': self.cleaned_data['first_name'],
                    'middle_name': self.cleaned_data['middle_name'],
                    'last_name': self.cleaned_data['last_name'],
                    'second_last_name': self.cleaned_data['second_last_name'],
                    'dni': self.cleaned_data['dni'],
                    'address': self.cleaned_data['address'],
                    'phone_number': self.cleaned_data['phone_number']
                }
            )
        return user

# --- Formulario de checkout ---
class CheckoutForm(forms.Form):
    address = forms.CharField(label='Dirección de entrega', widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(label='Ciudad', initial='Medellín', widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}))
    phone = forms.CharField(label='Teléfono', widget=forms.TextInput(attrs={'class': 'form-control'}))
    save_address = forms.BooleanField(label='Guardar dirección para futuras compras', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    notes = forms.CharField(label='Notas adicionales para el envío', required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

# --- Formulario de contacto ---
class ContactForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del mensaje'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mensaje', 'rows': 5}))

# --- Formulario de reseñas ---
class ReviewForm(forms.ModelForm):
    CALIFICACION_CHOICES = [
        (5.0, "5.0"), (4.5, "4.5"), (4.0, "4.0"),
        (3.5, "3.5"), (3.0, "3.0"), (2.5, "2.5"),
        (2.0, "2.0"), (1.5, "1.5"), (1.0, "1.0"), (0.5, "0.5"),
    ]
    calificacion = forms.ChoiceField(choices=CALIFICACION_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = Review
        fields = ['profesion', 'calificacion', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'profesion': forms.TextInput(attrs={'class': 'form-control'}),
        }
