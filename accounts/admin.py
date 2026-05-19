"""
Registro de modelos de accounts en el panel de administración.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Muestra el perfil de usuario dentro del panel de User."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['system_role', 'bio', 'avatar']


class UserAdmin(BaseUserAdmin):
    """Extiende el admin de User para mostrar el perfil inline."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff']

    def get_role(self, obj):
        try:
            return obj.profile.get_system_role_display()
        except UserProfile.DoesNotExist:
            return '-'
    get_role.short_description = 'Rol'


# Re-registrar UserAdmin con el inline del perfil
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'system_role', 'created_at']
    list_filter = ['system_role']
    search_fields = ['user__username', 'user__email']
