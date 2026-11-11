from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Address, Profile, User


@receiver(post_save, sender=User)
def criar_perfil_e_endereco(sender, instance, created, raw=False, **kwargs):
    """Todo usuário novo ganha um perfil e um endereço para preencher depois."""
    if created and not raw:
        Profile.objects.create(user=instance)
        Address.objects.create(user=instance)
