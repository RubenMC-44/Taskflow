"""
Endpoints API JSON para los componentes React de TaskFlow.
Devuelven datos en formato JSON consumidos desde el frontend con fetch().
"""
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Project, Task


@login_required
def api_projects(request):
    """
    GET /api/projects/
    Devuelve la lista de proyectos accesibles para el usuario autenticado.
    Soporta filtrado por ?search=, ?status= y ?role=.
    """
    user = request.user

    # Proyectos propios + en los que el usuario es miembro
    projects = Project.objects.filter(
        Q(owner=user) | Q(projectmember__user=user)
    ).distinct().select_related('owner')

    # Filtros opcionales por query params
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search:
        projects = projects.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    if status_filter:
        projects = projects.filter(status=status_filter)

    data = []
    for p in projects:
        data.append({
            'id': p.pk,
            'name': p.name,
            'description': p.description[:120] + '...' if len(p.description) > 120 else p.description,
            'status': p.status,
            'status_display': p.get_status_display(),
            'owner': p.owner.get_full_name() or p.owner.username,
            'is_public': p.is_public,
            'task_count': p.get_task_count(),
            'completed_tasks': p.get_completed_task_count(),
            'progress': p.get_progress_percentage(),
            'deadline': p.deadline.isoformat() if p.deadline else None,
            'created_at': p.created_at.strftime('%d/%m/%Y'),
            'url': f'/projects/{p.pk}/',
        })

    return JsonResponse({'projects': data, 'total': len(data)})


@login_required
def api_project_tasks(request, pk):
    """
    GET /api/projects/<pk>/tasks/
    Devuelve las tareas de un proyecto concreto.
    Soporta filtrado por ?status= y ?priority=.
    """
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Proyecto no encontrado'}, status=404)

    if not project.user_can_access(request.user):
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    tasks = project.tasks.select_related('assigned_to', 'created_by')

    # Filtros opcionales
    status_filter = request.GET.get('status', '').strip()
    priority_filter = request.GET.get('priority', '').strip()

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    data = []
    for t in tasks:
        data.append({
            'id': t.pk,
            'title': t.title,
            'description': t.description[:100] + '...' if len(t.description) > 100 else t.description,
            'status': t.status,
            'status_display': t.get_status_display(),
            'priority': t.priority,
            'priority_display': t.get_priority_display(),
            'assigned_to': t.assigned_to.get_full_name() or t.assigned_to.username if t.assigned_to else None,
            'due_date': t.due_date.isoformat() if t.due_date else None,
            'is_overdue': t.is_overdue(),
            'url': f'/tasks/{t.pk}/',
        })

    return JsonResponse({
        'project': project.name,
        'tasks': data,
        'total': len(data),
    })


@login_required
def api_dashboard_stats(request):
    """
    GET /api/dashboard/
    Devuelve estadísticas globales del usuario para el dashboard React.
    """
    user = request.user

    # Proyectos del usuario
    user_projects = Project.objects.filter(
        Q(owner=user) | Q(projectmember__user=user)
    ).distinct()

    # Tareas asignadas al usuario
    my_tasks = Task.objects.filter(assigned_to=user)

    # Tareas recientes (últimas 10)
    recent_tasks = my_tasks.select_related('project').order_by('-updated_at')[:10]

    recent_data = []
    for t in recent_tasks:
        recent_data.append({
            'id': t.pk,
            'title': t.title,
            'project': t.project.name,
            'status': t.status,
            'status_display': t.get_status_display(),
            'priority': t.priority,
            'priority_display': t.get_priority_display(),
            'is_overdue': t.is_overdue(),
            'url': f'/tasks/{t.pk}/',
        })

    stats = {
        'total_projects': user_projects.count(),
        'active_projects': user_projects.filter(status='active').count(),
        'total_tasks': my_tasks.count(),
        'todo': my_tasks.filter(status='todo').count(),
        'in_progress': my_tasks.filter(status='in_progress').count(),
        'review': my_tasks.filter(status='review').count(),
        'done': my_tasks.filter(status='done').count(),
        'overdue': sum(1 for t in my_tasks if t.is_overdue()),
        'recent_tasks': recent_data,
    }

    return JsonResponse(stats)
