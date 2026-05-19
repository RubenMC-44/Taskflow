"""
Registro de modelos de core en el panel de administración.
"""
from django.contrib import admin
from .models import Project, ProjectMember, Task, Comment


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    fields = ['user', 'role', 'joined_at']
    readonly_fields = ['joined_at']


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ['title', 'status', 'priority', 'assigned_to', 'due_date']
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'is_public', 'get_task_count', 'created_at']
    list_filter = ['status', 'is_public']
    search_fields = ['name', 'owner__username']
    inlines = [ProjectMemberInline, TaskInline]
    readonly_fields = ['created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()
    get_task_count.short_description = 'Tareas'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assigned_to', 'due_date']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'project__name', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at', 'created_by']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'task', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'task__title']
