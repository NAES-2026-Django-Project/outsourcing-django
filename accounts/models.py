from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.functional import cached_property

from .constants import ADMINISTRADOR, DESENVOLVEDOR, GERENTE


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Usuário autenticado por e-mail. O papel é definido pelos grupos do Django."""

    username = None
    email = models.EmailField('e-mail', unique=True)
    phone = models.CharField('telefone', max_length=20, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.email

    @cached_property
    def nomes_grupos(self):
        return set(self.groups.values_list('name', flat=True))

    @property
    def eh_administrador(self):
        return self.is_superuser or ADMINISTRADOR in self.nomes_grupos

    @property
    def eh_gerente(self):
        return GERENTE in self.nomes_grupos

    @property
    def eh_desenvolvedor(self):
        return DESENVOLVEDOR in self.nomes_grupos

    @property
    def papel(self):
        if self.eh_administrador:
            return ADMINISTRADOR
        if self.eh_gerente:
            return GERENTE
        return DESENVOLVEDOR


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='usuário')
    instagram_url = models.URLField('Instagram', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    linkedin_url = models.URLField('LinkedIn', blank=True)
    twitter_url = models.URLField('Twitter', blank=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'Perfil de {self.user}'


class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address', verbose_name='usuário')
    country = models.CharField('país', max_length=100, blank=True)
    state = models.CharField('estado', max_length=100, blank=True)
    city = models.CharField('cidade', max_length=100, blank=True)
    cep = models.CharField('CEP', max_length=20, blank=True)

    class Meta:
        verbose_name = 'endereço'
        verbose_name_plural = 'endereços'

    def __str__(self):
        return f'Endereço de {self.user}'
