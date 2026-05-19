"""
Vistas de la app core: home, dashboard, proyectos, tareas y comentarios.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Project, Task, Comment, ProjectMember
from .forms import ProjectForm, TaskForm, CommentForm, AddMemberForm


# ─────────────────────────────────────────────
#  VISTAS GENERALES
# ─────────────────────────────────────────────

def home_view(request):
    """Página de inicio pública."""
    public_projects = Project.objects.filter(is_public=True, status='active')[:6]
    return render(request, 'home.html', {'public_projects': public_projects})


@login_required
def dashboard_view(request):
    """
    Dashboard principal del usuario autenticado.
    Muestra estadísticas y tareas pendientes.
    Se usa React para la visualización de tareas con filtros en tiempo real.
    """
    user = request.user

    # Proyectos donde el usuario es propietario o miembro
    user_projects = Project.objects.filter(
        Q(owner=user) | Q(projectmember__user=user)
    ).distinct()

    # Tareas asignadas al usuario
    my_tasks = Task.objects.filter(assigned_to=user).select_related('project')

    # Estadísticas globales para el usuario
    stats = {
        'total_projects': user_projects.count(),
        'active_projects': user_projects.filter(status='active').count(),
        'total_tasks': my_tasks.count(),
        'todo_tasks': my_tasks.filter(status='todo').count(),
        'in_progress_tasks': my_tasks.filter(status='in_progress').count(),
        'done_tasks': my_tasks.filter(status='done').count(),
    }

    return render(request, 'core/dashboard.html', {
        'stats': stats,
        'user_projects': user_projects[:5],
    })


# ─────────────────────────────────────────────
#  PROYECTOS
# ─────────────────────────────────────────────

@login_required
def project_list_view(request):
    """
    Lista de proyectos accesibles para el usuario.
    Incluye el componente React para búsqueda y filtrado en tiempo real.
    """
    return render(request, 'core/project_list.html')


@login_required
def project_detail_view(request, pk):
    """Detalle de un proyecto con sus tareas y miembros."""
    project = get_object_or_404(Project, pk=pk)

    if not project.user_can_access(request.user):
        messages.error(request, 'No tienes permiso para ver este proyecto.')
        return redirect('project_list')

    tasks = project.tasks.select_related('assigned_to', 'created_by')
    members = project.projectmember_set.select_related('user')
    add_member_form = AddMemberForm()

    # Agrupar tareas por estado
    tasks_by_status = {
        'todo': tasks.filter(status='todo'),
        'in_progress': tasks.filter(status='in_progress'),
        'review': tasks.filter(status='review'),
        'done': tasks.filter(status='done'),
    }

    return render(request, 'core/project_detail.html', {
        'project': project,
        'tasks_by_status': tasks_by_status,
        'members': members,
        'add_member_form': add_member_form,
        'can_edit': project.user_can_edit(request.user),
    })


@login_required
def project_create_view(request):
    """Crear un nuevo proyecto."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Proyecto "{project.name}" creado correctamente.')
            return redirect('project_detail', pk=project.pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = ProjectForm()

    return render(request, 'core/project_form.html', {
        'form': form,
        'title': 'Nuevo proyecto',
        'button_text': 'Crear proyecto',
    })


@login_required
def project_edit_view(request, pk):
    """Editar un proyecto existente."""
    project = get_object_or_404(Project, pk=pk)

    if not project.user_can_edit(request.user):
        messages.error(request, 'No tienes permiso para editar este proyecto.')
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Proyecto "{project.name}" actualizado.')
            return redirect('project_detail', pk=pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'core/project_form.html', {
        'form': form,
        'project': project,
        'title': f'Editar: {project.name}',
        'button_text': 'Guardar cambios',
    })


@login_required
def project_delete_view(request, pk):
    """Eliminar un proyecto."""
    project = get_object_or_404(Project, pk=pk)

    if not project.user_can_edit(request.user):
        messages.error(request, 'No tienes permiso para eliminar este proyecto.')
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'Proyecto "{name}" eliminado.')
        return redirect('project_list')

    return render(request, 'core/project_confirm_delete.html', {'project': project})


@login_required
def project_add_member_view(request, pk):
    """Añadir un miembro a un proyecto."""
    project = get_object_or_404(Project, pk=pk)

    if not project.user_can_edit(request.user):
        messages.error(request, 'No tienes permiso para gestionar miembros.')
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            role = form.cleaned_data['role']
            user_to_add = User.objects.get(username=username)

            if user_to_add == project.owner:
                messages.warning(request, 'Este usuario ya es el propietario del proyecto.')
            elif ProjectMember.objects.filter(project=project, user=user_to_add).exists():
                messages.warning(request, f'"{username}" ya es miembro de este proyecto.')
            else:
                ProjectMember.objects.create(project=project, user=user_to_add, role=role)
                messages.success(request, f'"{username}" añadido como {dict(ProjectMember.ROLE_CHOICES)[role]}.')
        else:
            # Mostrar el primer error del formulario como mensaje flash
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                break

    return redirect('project_detail', pk=pk)


@login_required
def project_remove_member_view(request, pk, user_id):
    """Eliminar un miembro de un proyecto."""
    project = get_object_or_404(Project, pk=pk)

    if not project.user_can_edit(request.user):
        messages.error(request, 'No tienes permiso para gestionar miembros.')
        return redirect('project_detail', pk=pk)

    member = get_object_or_404(ProjectMember, project=project, user_id=user_id)
    username = member.user.username
    member.delete()
    messages.success(request, f'{username} eliminado del proyecto.')
    return redirect('project_detail', pk=pk)


# ─────────────────────────────────────────────
#  TAREAS
# ─────────────────────────────────────────────

@login_required
def task_detail_view(request, pk):
    """Detalle de una tarea con comentarios."""
    task = get_object_or_404(Task, pk=pk)

    if not task.project.user_can_access(request.user):
        messages.error(request, 'No tienes permiso para ver esta tarea.')
        return redirect('project_list')

    comments = task.comments.select_related('author')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comentario añadido.')
            return redirect('task_detail', pk=pk)

    return render(request, 'core/task_detail.html', {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'can_edit': task.project.user_can_edit(request.user),
    })


@login_required
def task_create_view(request, project_pk):
    """Crear una nueva tarea dentro de un proyecto."""
    project = get_object_or_404(Project, pk=project_pk)

    if not project.user_can_access(request.user):
        messages.error(request, 'No tienes permiso para añadir tareas a este proyecto.')
        return redirect('project_list')

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            messages.success(request, f'Tarea "{task.title}" creada.')
            return redirect('project_detail', pk=project_pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = TaskForm(project=project)

    return render(request, 'core/task_form.html', {
        'form': form,
        'project': project,
        'title': 'Nueva tarea',
        'button_text': 'Crear tarea',
    })


@login_required
def task_edit_view(request, pk):
    """Editar una tarea existente."""
    task = get_object_or_404(Task, pk=pk)

    if not task.project.user_can_edit(request.user):
        messages.error(request, 'No tienes permiso para editar esta tarea.')
        return redirect('task_detail', pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=task.project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tarea "{task.title}" actualizada.')
            return redirect('task_detail', pk=pk)
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = TaskForm(instance=task, project=task.project)

    return render(request, 'core/task_form.html', {
        'form': form,
        'task': task,
        'project': task.project,
        'title': f'Editar tarea',
        'button_text': 'Guardar cambios',
    })


@login_required
def task_delete_view(request, pk):
    """Eliminar una tarea."""
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk

    if not task.project.user_can_edit(request.user):
        messages.error(request, 'No tienes permiso para eliminar esta tarea.')
        return redirect('task_detail', pk=pk)

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Tarea "{title}" eliminada.')
        return redirect('project_detail', pk=project_pk)

    return render(request, 'core/task_confirm_delete.html', {'task': task})


@login_required
def task_update_status_view(request, pk):
    """Actualizar el estado de una tarea (AJAX / formulario rápido)."""
    task = get_object_or_404(Task, pk=pk)

    if not task.project.user_can_access(request.user):
        messages.error(request, 'No tienes permiso.')
        return redirect('dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = dict(Task.STATUS_CHOICES).keys()
        if new_status in valid_statuses:
            task.status = new_status
            task.save()
            messages.success(request, 'Estado actualizado.')

    return redirect('task_detail', pk=pk)
