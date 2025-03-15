from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.username == 'admin':
            admin_group = Group.objects.get(name='Administrador')
            instance.groups.add(admin_group)
        else:
            cliente_group = Group.objects.get(name='Cliente')
            instance.groups.add(cliente_group)

# @receiver(post_save, sender=User)
# def assign_default_group(sender, instance, created, **kwargs):
#     if created and not instance.groups.exists():
#         cliente_group = Group.objects.get(name='Cliente')
#         instance.groups.add(cliente_group)
