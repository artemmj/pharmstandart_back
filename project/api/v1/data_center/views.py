from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.helpers import viewsets
from apps.fs2_api.services.process_support_requests import (
    init_support_request, send_support_request, add_attach_to_support_request,
)
from apps.data_center.models import DCEmployee, DCDepartment
from . import serializers
from . import filters


class DataCenterViewSet(viewsets.ExtendedViewSet):
    serializer_class = serializers.InitSupportRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        pass

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.InitSupportRequestMKSerializer})
    @action(methods=['get'], detail=False, url_path='init-support-request', url_name='init-support-request')
    def get_support_request(self, request):
        result = init_support_request(request)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.EmptySerializer},
        request_body=serializers.SendSupportRequestSerializer)
    @action(methods=['post'], detail=False, url_path='send-support-request', url_name='send-support-request')
    def _send_support_request(self, request):
        send_support_request(request)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.AddAttachSupReqResultSerializer},
        request_body=serializers.AddAttachToSupportRequestSerializer)
    @action(methods=['post'], detail=False, url_path='add-attach-support-req', url_name='add-attach-support-req')
    def _add_attach_to_support_request(self, request):
        add_attach_to_support_request(request)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class DCEmployeesViewSet(viewsets.ExtendedModelViewSet):
    queryset = DCEmployee.objects.all()
    serializer_class = serializers.DCUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    ordering_fields = ('name', 'department', 'job_title',)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.DCEmployeeFilterSet

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.DCListEmployeeResponseSerializer})
    def list(self, request):
        serializer = self.get_serializer(self.filter_queryset(self.get_queryset()), many=True)
        return_data = {
            'count': len(serializer.data),
            'results': serializer.data
        }
        return Response(return_data, status=status.HTTP_200_OK)


class DCOrgStructureViewSet(viewsets.ExtendedModelViewSet):
    queryset = DCDepartment.objects.all().order_by('id')
    serializer_class = serializers.DCDepartmentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    ordering_fields = ('title',)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = filters.DCDepartmentFilterSet

    def list(self, request):
        query_srlzer = serializers.GetDCDeptsQuerySerializer(
            data=request.query_params,
        )
        query_srlzer.is_valid(raise_exception=True)

        serializer = self.get_serializer(self.filter_queryset(self.get_queryset()), many=True)
        return_data = {
            'count': len(serializer.data),
            'results': serializer.data
        }
        return Response(return_data, status=status.HTTP_200_OK)
