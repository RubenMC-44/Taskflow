"""
URLs de la app core.
"""
from django.urls import path
from . import views, api

urlpatterns = [
    # ── General ──────────────────────────────────────
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ── Proyectos ─────────────────────────────────────
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/new/', views.project_create_view, name='project_create'),
    path('projects/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit_view, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='project_delete'),
    path('projects/<int:pk>/add-member/', views.project_add_member_view, name='project_add_member'),
    path('projects/<int:pk>/remove-member/<int:user_id>/', views.project_remove_member_view, name='project_remove_member'),

    # ── Tareas ────────────────────────────────────────
    path('projects/<int:project_pk>/tasks/new/', views.task_create_view, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit_view, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete_view, name='task_delete'),
    path('tasks/<int:pk>/status/', views.task_update_status_view, name='task_update_status'),

    # ── API JSON para React ───────────────────────────
    path('api/projects/', api.api_projects, name='api_projects'),
    path('api/projects/<int:pk>/tasks/', api.api_project_tasks, name='api_project_tasks'),
    path('api/dashboard/', api.api_dashboard_stats, name='api_dashboard'),
]
