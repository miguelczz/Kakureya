from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import UserProfile

@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.username == 'admin':
            admin_group = Group.objects.get(name='Administrador')
            instance.groups.add(admin_group)
        else:
            cliente_group = Group.objects.get(name='Cliente')
            instance.groups.add(cliente_group)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, email=instance.email)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


# Se agregaron nuevas señales para crear y guardar el perfil de usuario
# y asignar el grupo correspondiente al usuario creado.

# La señal assign_user_group verifica si el usuario creado es el administrador
# y le asigna el grupo 'Administrador', en caso contrario le asigna el grupo 'Cliente'.

# La señal create_user_profile crea un perfil de usuario para el usuario creado.

# La señal save_user_profile guarda el perfil de usuario creado.
#---------------------------------------------------------------
# @receiver(post_save, sender=User)
# def assign_default_group(sender, instance, created, **kwargs):
#     if created and not instance.groups.exists():
#         cliente_group = Group.objects.get(name='Cliente')
#         instance.groups.add(cliente_group)
