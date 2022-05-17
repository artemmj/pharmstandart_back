from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import serializers, exceptions
from rest_framework.views import exception_handler as base_exception_handler


class ErrorResponseSerializer(serializers.Serializer):
    status_code = serializers.IntegerField()
    errors = serializers.CharField()


def exception_handler(exc, context):
    response = base_exception_handler(exc, context)
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if response is not None:
        data = {
            'status_code': exc.status_code,
            'errors': {},
        }
        if isinstance(exc.detail, list):
            data['errors'] = exc.detail
        elif isinstance(exc.detail, dict):
            data['errors'] = exc.detail
        else:
            data['errors'] = exc.detail
        response.data = data
    return response
