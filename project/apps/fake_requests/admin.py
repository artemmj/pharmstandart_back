from django.contrib import admin

from .models import FakeRequest


@admin.register(FakeRequest)
class FakeRequestAdmin(admin.ModelAdmin):
    pass
