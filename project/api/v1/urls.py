from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from .celery.views import CeleryResultView

from .user.views import UserViewSet, PharmUserViewSet
from .file.views import FileViewSet
from .documents.views import DocumentViewSet
from .tasks_errands.views import TasksErrandsViewSet
from .homepage.views import HomepageViewSet
from .news.views import CompanyNewsViewSet, PharmNewsViewSet
from .data_center.views import (
    DataCenterViewSet, DCEmployeesViewSet, DCOrgStructureViewSet,
)
from .elibrary.views import ELibraryApiView
from .fake_requests.views import FakeRequestViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'pharm-users', PharmUserViewSet, basename='pharm-users')
router.register(r'file', FileViewSet, basename='file')
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'tasks', TasksErrandsViewSet, basename='tasks')
router.register(r'homepage', HomepageViewSet, basename='homepage')
router.register(r'news-company', CompanyNewsViewSet, basename='news_company')
router.register(r'news-pharm', PharmNewsViewSet, basename='news_pharm')
router.register(r'elibrary', ELibraryApiView, basename='elibrary')
router.register(r'datacenter/employees', DCEmployeesViewSet, basename='datacenter/employees')
router.register(r'datacenter/org-structure', DCOrgStructureViewSet, basename='datacenter/org-structure')
router.register(r'datacenter', DataCenterViewSet, basename='datacenter')
router.register(r'fake-request', FakeRequestViewSet, basename='fake_request')


schema_view = get_schema_view(
    openapi.Info(
        title='Pharm Standart API',
        default_version='v1',
        description='Pharm Standart Proxy API',
    ),
    # validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger(<str:format>.json|.yaml)/', schema_view.without_ui(), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc'), name='schema-redoc'),
    path('celery/result/<pk>/', CeleryResultView.as_view()),
    path('', include((router.urls, 'api-root')), name='api-root'),
]
