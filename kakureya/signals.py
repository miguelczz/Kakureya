from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import UserProfile
from django.core.exceptions import ObjectDoesNotExist

# Asigna el grupo correspondiente cuando se crea un nuevo usuario
@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.email == 'kakureyagroup@gmail.com':
            admin_group = Group.objects.get(name='Administrador')
            instance.groups.add(admin_group)
        else:
            cliente_group = Group.objects.get(name='Cliente')
            instance.groups.add(cliente_group)

# Guarda el perfil del usuario cuando se guarda el modelo User
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

# Crea el perfil del usuario automáticamente si no existe
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            instance.userprofile
        except ObjectDoesNotExist:
            UserProfile.objects.create(user=instance, email=instance.email)
            print(f"Perfil creado automáticamente para {instance.email}")
