from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Review

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

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class CheckoutForm(forms.Form):
    address = forms.CharField(
        label='Dirección de entrega', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    city = forms.CharField(
        label='Ciudad', 
        initial='Medellín',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True})
    )
    phone = forms.CharField(
        label='Teléfono', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    save_address = forms.BooleanField(
        label='Guardar dirección para futuras compras', 
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        label='Notas adicionales para el envío', 
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
class ContactForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titulo del mensaje'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mensaje', 'rows': 5})
    )

class ReviewForm(forms.ModelForm):
    CALIFICACION_CHOICES = [
        (5.0, "5.0"),
        (4.5, "4.5"),
        (4.0, "4.0"),
        (3.5, "3.5"),
        (3.0, "3.0"),
        (2.5, "2.5"),
        (2.0, "2.0"),
        (1.5, "1.5"),
        (1.0, "1.0"),
        (0.5, "0.5"),
    ]

    calificacion = forms.ChoiceField(choices=CALIFICACION_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = Review
        fields = ['nombre', 'profesion', 'calificacion', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'profesion': forms.TextInput(attrs={'class': 'form-control'}),
        }
