import os

from django.conf import settings

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.helpers import viewsets
from api.v1.documents import serializers
from apps.fs2_api.services import (
    get_all_entities, get_detailed_entity, prepare_action, commit_action,
    rollback_action, send_attach_action, check_dss_status,
    get_statuses_from_documents, get_filtered_documents_by_status,
)


class DocumentViewSet(viewsets.ExtendedViewSet):
    serializer_class = serializers.ListAllDocumentsSerializer
    serializer_class_map = {
        'list': serializers.ListAllDocumentsSerializer,
        'retrieve': serializers.DetailedDocumentSerializer,
        'prepare_action': serializers.PrepareSpecActionSerializer,
        'commit_action': serializers.CommitActionSerializer,
        'rollback_action': serializers.CommitActionSerializer,
        'send_attach_action': serializers.SendAttachActionSerializer,
        'check_dss_status': serializers.CheckDssStatusSerializer,
    }
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        pass  # для свагера

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.ListAllDocumentsSerializer})
    def list(self, request):
        query_serializer = serializers.DocumentsListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        documents = get_all_entities(user=request.user, query_params=query_serializer.data)
        page = self.paginate_queryset(documents)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(documents, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.DetailedDocumentSerializer})
    def retrieve(self, request, pk=None):
        document = get_detailed_entity(request.user, pk)
        if not document:
            raise NotFound('Документ не найден')
        return Response(document, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.DocsStatusesSerializer})
    @action(methods=['get'], detail=False, url_path='statuses', url_name='statuses')
    def get_docs_statuses(self, request):
        documents = get_all_entities(request.user)
        return Response(get_statuses_from_documents(documents))

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.DocsStatusesSerializer})
    @action(methods=['get'], detail=False, url_path='get-by', url_name='get-by')
    def get_documents_by_state(self, request):
        query_serializer = serializers.DocumentsStatusesRequestSerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        documents = get_all_entities(request.user, query_params=query_serializer.data)
        return Response(get_filtered_documents_by_status(
            documents,
            query_serializer.validated_data['status']),
        )

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.PrepareSpecActionResultSerializer},
        request_body=serializers.PrepareSpecActionSerializer,)
    @action(methods=['post'], detail=False, url_path='prepare-action', url_name='prepare-action')
    def _prepare_action(self, request):
        serializer = serializers.PrepareSpecActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = prepare_action(serializer.data, request.user)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.CommitActionResultSerializer},
        request_body=serializers.CommitActionSerializer,)
    @action(methods=['post'], detail=False, url_path='commit-action', url_name='commit-action')
    def _commit_action(self, request):
        serializer = serializers.CommitActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = commit_action(serializer.data, request.user)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.RollbackActionResultSerializer},
        request_body=serializers.RollbackActionSerializer,)
    @action(methods=['post'], detail=False, url_path='rollback-action', url_name='rollback-action')
    def _rollback_action(self, request):
        serializer = serializers.RollbackActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = rollback_action(serializer.data, request.user)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.SendAttachActionResultSerializer},
        request_body=serializers.SendAttachActionSerializer)
    @action(methods=['post'], detail=False, url_path='send-attach', url_name='send-attach')
    def _send_attach_action(self, request):
        serializer = serializers.SendAttachActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not os.path.exists(settings.MEDIA_URL + '/attachs'):
            os.makedirs(settings.MEDIA_URL + '/attachs')

        up_file = request.data.get('file')
        file_dest = settings.MEDIA_URL + 'attachs/' + up_file.name
        dest = open(file_dest, 'wb+')
        for chunk in up_file.chunks():
            dest.write(chunk)
        dest.close()

        data = serializer.data.copy()
        data['filepath'] = file_dest
        result = send_attach_action(data, request.user)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.DssStatusSerializer},
        request_body=serializers.CheckDssStatusSerializer)
    @action(methods=['post'], detail=False, url_path='check-dss-status', url_name='check-dss-status')
    def _check_dss_status(self, request):
        serializer = serializers.CheckDssStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = check_dss_status(serializer.data, request.user)
        return Response(result, status=status.HTTP_200_OK)
