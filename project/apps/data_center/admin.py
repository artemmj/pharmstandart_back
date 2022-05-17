from django.contrib import admin

from .models import DCEmployee, DCDepartment


@admin.register(DCEmployee)
class DSEmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'login', 'work_email', 'department',)


@admin.register(DCDepartment)
class DCDepartmentAdmin(admin.ModelAdmin):
    ordering = ('title',)
    list_display = ('id', 'title', 'parent',)
