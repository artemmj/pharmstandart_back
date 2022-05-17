# from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import PharmUser, PharmSession

User = get_user_model()


class CustomUserCreationFrom(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'phone',)


class CustomUserChangeFrom(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'phone',)


class UserAdmin(UserAdmin):
    add_form = CustomUserCreationFrom
    form = CustomUserChangeFrom
    model = User
    list_display = ('email', 'phone', 'username', 'is_test_user',)
    list_filter = ('email', 'phone', 'username',)

    fieldsets = (
        (None, {'fields': (
            'is_active', 'email', 'phone', 'username', 'first_name',
            'last_name', 'middle_name', 'image', 'pharm_session')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff',)}),
        ('Datas', {'fields': ('last_login', 'date_joined',)}),
    )

    search_fields = ('email', 'phone', 'username')
    ordering = ('email', 'phone', 'username')


class PharmUserAdmin(admin.ModelAdmin):
    model = PharmUser
    list_display = ('email', 'fio', 'username',)


class PharmSessionAdmin(admin.ModelAdmin):
    model = PharmSession


admin.site.register(User, UserAdmin)
admin.site.register(PharmUser, PharmUserAdmin)
admin.site.register(PharmSession, PharmSessionAdmin)
