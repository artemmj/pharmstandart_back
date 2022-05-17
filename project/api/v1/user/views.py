import os
import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework_jwt.serializers import (
    RefreshJSONWebTokenSerializer, VerifyJSONWebTokenSerializer,
    JSONWebTokenSerializer,
)
from rest_framework_jwt.settings import api_settings
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend

from apps.helpers.exceptions import ErrorResponseSerializer
from apps.helpers.viewsets import RUDExtendedModelViewSet
from apps.helpers.batchmixin import DeleteBatchMixin
from apps.user.managers import UserQuerysetManager
from apps.user.models import PharmUser
from .filters import UserFilterSet
from . import serializers, services

User = get_user_model()
logger = logging.getLogger()
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class UserViewSet(RUDExtendedModelViewSet, DeleteBatchMixin):
    queryset = User.objects.all()
    serializer_class = serializers.UserWriteSerializer
    serializer_class_map = {
        'list': serializers.UserReadSerializer,
        'retrieve': serializers.UserReadSerializer,
        'me': serializers.UserReadSerializer,
        'login': JSONWebTokenSerializer,
        'refresh': RefreshJSONWebTokenSerializer,
        'verify': VerifyJSONWebTokenSerializer,
        'change_password': serializers.UserChangePasswordSerializer,
        'compact': serializers.UserCompactSerializer,
    }
    permission_map = {
        'login': permissions.AllowAny,
        'test': permissions.AllowAny,
        'registration': permissions.AllowAny,
    }
    permission_classes = (permissions.IsAuthenticated,)
    search_fields = ('email', 'phone', 'first_name', 'middle_name', 'last_name')
    ordering_fields = ('email', 'phone', 'first_name', 'middle_name', 'last_name')
    filterset_class = UserFilterSet
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    default_responses = {
        200: serializers.UserLoginResponseSerializer,
        400: ErrorResponseSerializer,
        410: ErrorResponseSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()

        return UserQuerysetManager().get_queryset(user)

    def _auth(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.object.get('token')
        return Response({'token': token})

    @swagger_auto_schema(responses=default_responses)
    @action(methods=['post'], detail=False)
    def login(self, request):
        return Response(services.auth_via_pharm_apis(request))

    @swagger_auto_schema(responses=default_responses)
    @action(methods=['post'], detail=False)
    def refresh(self, request):
        return self._auth(request)

    @swagger_auto_schema(responses=default_responses)
    @action(methods=['post'], detail=False)
    def verify(self, request):
        return self._auth(request)

    @action(methods=['post'], detail=False)
    def registration(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            error_message = {
                'detail': 'Ошибка при попытке регистрации пользователя',
                'source': exc,
                'status': 400,
            }
            raise ValidationError(error_message)

        user = serializer.save()
        data = serializers.UserReadSerializer(instance=user, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: serializers.UserReadSerializer, 400: ErrorResponseSerializer})
    @action(methods=['get'], detail=False)
    def me(self, request, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: serializers.UserChangePasswordSerializer, 400: ErrorResponseSerializer})
    @action(methods=['post'], detail=False, url_path='change-password')
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, instance=request.user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = serializers.UserReadSerializer(instance=user).data
        return Response(data)

    @action(methods=['get'], detail=False)
    def compact(self, request):
        return super().list(request)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.GetVacationDaysCountSerializer})
    @action(methods=['get'], detail=False, url_path='available-vacation-days', url_name='available-vacation-days')
    def get_valation_days_count(self, request):
        return Response(services.get_vacation_count_actual_days(request.user))

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.GetVacationScheduleSerializer})
    @action(
        methods=['get'], detail=False, url_path='vacation-schedule', url_name='vacation-schedule',
        permission_classes=(permissions.IsAuthenticated,))
    def get_vacation_schedule(self, request):
        return Response(services.get_vacation_schedule(request.user))

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.RequestsForDocumentsSerializer}, methods=['get'])
    @action(
        methods=['get'], detail=False, url_path='get-requests-for-documents', url_name='get-requests-for-documents')
    def get_requests_for_documents(self, request):
        requests = services.get_requests_for_documents(request.user)
        page = self.paginate_queryset(requests)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(requests, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.RequestOrgTypesSerializer})
    @action(methods=['get'], detail=False, url_path='get-request-org-types', url_name='get-request-org-types')
    def get_request_org_types(self, request):
        types = services.get_request_org_types(request.user)
        page = self.paginate_queryset(types)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(types, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.SendRequestDocumentSerializerResult},
        request_body=serializers.SendRequestDocumentSerializer)
    @action(methods=['post'], detail=False, url_path='send-request-document', url_name='send-request-document')
    def send_request_document(self, request):
        serializer = serializers.SendRequestDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not os.path.exists(settings.MEDIA_URL + 'doc_requests'):
            os.makedirs(settings.MEDIA_URL + 'doc_requests')

        data = serializer.data.copy()
        up_files = request.FILES.getlist('files')
        if up_files:
            dests = list()
            for up_file in up_files:
                file_dest = settings.MEDIA_URL + 'doc_requests/' + up_file.name
                dest = open(file_dest, 'wb+')
                for chunk in up_file.chunks():
                    dest.write(chunk)
                dest.close()
                dests.append(file_dest)
            data['files'] = dests

        result = services.send_request_document(request, data)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.DatesForPaySheetSerializer})
    @action(methods=['get'], detail=False, url_path='sheet-months', url_name='sheet-months')
    def get_dates_for_pay_sheet(self, request):
        return Response(services.get_dates_for_pay_sheets(request.user))

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: None},
        request_body=serializers.SendPaySheetRequestSerializer)
    @action(methods=['post'], detail=False, url_path='send-pay-sheet', url_name='send-pay-sheet')
    def send_pay_sheet_by_month(self, request):
        serializer = serializers.SendPaySheetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.send_pay_sheet(request.user, serializer.data['month'])
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.GetUflexBase64Serializer})
    @action(methods=['get'], detail=False, url_path='get-uflex-base64', url_name='get-uflex-base64')
    def get_uflex_base64(self, request):
        base64data = services.generate_sso_saml_uflex(request)
        return Response({'base64data': base64data}, status=status.HTTP_200_OK)


class PharmUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PharmUser.objects.all()
    serializer_class = serializers.PharmUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    filterset_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('pharm_id', 'email', 'fio', 'phone1', 'phone2', 'username')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
