"""
Formularios de la app core: proyectos, tareas y comentarios.
"""
from django import forms
from .models import Project, Task, Comment, ProjectMember
from django.contrib.auth.models import User


class ProjectForm(forms.ModelForm):
    """Formulario para crear y editar proyectos."""

    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'is_public', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proyecto',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe brevemente el proyecto...',
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'status': 'Estado',
            'is_public': 'Proyecto público (visible para todos)',
            'deadline': 'Fecha límite',
        }


class TaskForm(forms.ModelForm):
    """Formulario para crear y editar tareas."""

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada de la tarea...',
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'assigned_to': 'Asignar a',
            'status': 'Estado',
            'priority': 'Prioridad',
            'due_date': 'Fecha de entrega',
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar los usuarios asignables: solo miembros del proyecto
        if project:
            member_ids = list(project.projectmember_set.values_list('user_id', flat=True))
            member_ids.append(project.owner_id)
            self.fields['assigned_to'].queryset = User.objects.filter(id__in=member_ids)
        else:
            self.fields['assigned_to'].queryset = User.objects.none()
        self.fields['assigned_to'].empty_label = '-- Sin asignar --'


class CommentForm(forms.ModelForm):
    """Formulario para añadir comentarios a tareas."""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe un comentario...',
            }),
        }
        labels = {
            'content': '',
        }


class AddMemberForm(forms.Form):
    """Formulario para añadir un miembro a un proyecto."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
        }),
        label='Usuario'
    )
    role = forms.ChoiceField(
        choices=ProjectMember.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Rol'
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f'No existe ningún usuario con el nombre "{username}".')
        return username
