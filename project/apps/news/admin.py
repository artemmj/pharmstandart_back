from django.contrib import admin

from .models import PharmMarketArticle, CompanyArticle, Birthday, PersonnelChange


@admin.register(PharmMarketArticle)
class PharmMarketArticleAdmin(admin.ModelAdmin):
    list_display = ('portal_id', 'publish_date', 'title',)
    fieldsets = (
        (None, {'fields': (
            'title', 'portal_id', 'publish_date', 'is_main', 'published',
            'description', 'image', 'image_icon',)}),
    )
    search_fields = ('title',)
    ordering = ('publish_date',)


@admin.register(CompanyArticle)
class CompanyArticleAdmin(admin.ModelAdmin):
    list_display = ('portal_id', 'publish_date', 'title',)
    fieldsets = (
        (None, {'fields': (
            'title', 'portal_id', 'publish_date', 'is_main', 'published',
            'description', 'image', 'image_icon',)}),
    )
    search_fields = ('title',)
    ordering = ('publish_date',)


@admin.register(Birthday)
class BirthdayAdmin(admin.ModelAdmin):
    ...


@admin.register(PersonnelChange)
class PersonnelChangeAdmin(admin.ModelAdmin):
    ...
