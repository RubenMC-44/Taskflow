"""
Modelos principales de TaskFlow:
  - Project: proyecto de trabajo
  - ProjectMember: relación usuario-proyecto con rol
  - Task: tarea dentro de un proyecto
  - Comment: comentario en una tarea
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    """Representa un proyecto de trabajo."""

    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Estado'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Propietario'
    )
    members = models.ManyToManyField(
        User,
        through='ProjectMember',
        related_name='member_projects',
        blank=True
    )
    is_public = models.BooleanField(default=False, verbose_name='Público')
    deadline = models.DateField(null=True, blank=True, verbose_name='Fecha límite')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_task_count(self):
        return self.tasks.count()

    def get_completed_task_count(self):
        return self.tasks.filter(status='done').count()

    def get_progress_percentage(self):
        total = self.get_task_count()
        if total == 0:
            return 0
        return int((self.get_completed_task_count() / total) * 100)

    def user_can_access(self, user):
        """Comprueba si un usuario puede ver este proyecto."""
        if self.is_public:
            return True
        if not user.is_authenticated:
            return False
        return (
            self.owner == user
            or self.projectmember_set.filter(user=user).exists()
            or user.is_superuser
        )

    def user_can_edit(self, user):
        """Comprueba si un usuario puede editar este proyecto."""
        if not user.is_authenticated:
            return False
        return (
            self.owner == user
            or self.projectmember_set.filter(user=user, role='lead').exists()
            or user.is_superuser
        )


class ProjectMember(models.Model):
    """Relación entre un usuario y un proyecto, con su rol."""

    ROLE_CHOICES = [
        ('lead', 'Project Lead'),
        ('member', 'Miembro'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name='Rol'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Miembro del proyecto'
        verbose_name_plural = 'Miembros del proyecto'
        unique_together = ('project', 'user')

    def __str__(self):
        return f'{self.user.username} — {self.project.name} ({self.get_role_display()})'


class Task(models.Model):
    """Representa una tarea dentro de un proyecto."""

    STATUS_CHOICES = [
        ('todo', 'Por hacer'),
        ('in_progress', 'En progreso'),
        ('review', 'En revisión'),
        ('done', 'Completada'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descripción')
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Proyecto'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Asignada a'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='Creada por'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name='Estado'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Prioridad'
    )
    due_date = models.DateField(null=True, blank=True, verbose_name='Fecha de entrega')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.project.name}]'

    def is_overdue(self):
        """Comprueba si la tarea está vencida."""
        if self.due_date and self.status != 'done':
            return self.due_date < timezone.now().date()
        return False


class Comment(models.Model):
    """Comentario en una tarea."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Tarea'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Autor'
    )
    content = models.TextField(verbose_name='Contenido')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']

    def __str__(self):
        return f'Comentario de {self.author.username} en "{self.task.title}"'
