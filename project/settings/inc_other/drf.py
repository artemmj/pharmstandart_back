# https://github.com/encode/django-rest-framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_RATES': {},
    'OVERIDE_THROTTLE_RATES': {},
    'DEFAULT_PAGINATION_CLASS': 'apps.helpers.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'apps.helpers.exceptions.exception_handler',
}
