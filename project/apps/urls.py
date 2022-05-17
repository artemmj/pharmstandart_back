from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

admin.site.site_title = 'Django Admin'
admin.site.site_header = 'Django Admin'
admin.site.index_title = 'Django Admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(('api.v1.urls', 'api_v1')), name='api_v1'),
]


if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += \
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
