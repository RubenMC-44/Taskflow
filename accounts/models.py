"""
Modelos de la app accounts.
Extiende el usuario de Django con un perfil adicional.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Perfil extendido del usuario.
    Se crea automáticamente cuando se registra un nuevo usuario.
    """
    SYSTEM_ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('user', 'Usuario'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )
    system_role = models.CharField(
        max_length=20,
        choices=SYSTEM_ROLE_CHOICES,
        default='user',
        verbose_name='Rol en el sistema'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Biografía'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil de {self.user.username}'

    def is_admin(self):
        """Comprueba si el usuario tiene rol de administrador."""
        return self.system_role == 'admin' or self.user.is_superuser


# --- Señal: crear perfil automáticamente al crear usuario ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un UserProfile cuando se registra un nuevo User."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el UserProfile cuando se guarda el User."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
