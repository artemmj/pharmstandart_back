from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from constance import config as constance_lib

from apps.homepage.models import Slider
from apps.helpers import viewsets
from . import serializers
from . import services


class HomepageViewSet(viewsets.ExtendedViewSet):
    serializer_class = serializers.HomepageFullDocumentsSerializer
    serializer_class_map = {
        'get_tasks_count': serializers.HomepageGetTasksCountSerializer,
        'get_mails_count': serializers.HomepageGetMailsCountSerializer,
        'documents': serializers.HomepageFullDocumentsSerializer,
        'sliders': serializers.HomepageSlidersSerializer,
        'tolls': serializers.HomepageTollsSerializer,
    }
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        pass  # для свагера

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.HomepageGetTasksCountSerializer})
    @action(methods=['get'], detail=False, url_path='get-tasks-count', url_name='get-tasks-count')
    def get_tasks_count(self, request):
        result = services.get_tasks_count(request.user)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.HomepageGetMailsCountSerializer})
    @action(methods=['get'], detail=False, url_path='get-mails-count', url_name='get-mails-count')
    def get_mails_count(self, request):
        result = services.get_mails_count(request.user)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.HomepageFullDocumentsSerializer})
    @action(methods=['get'], detail=False, url_path='documents', url_name='documents')
    def documents(self, request):
        result = services.retrieve_documents(request.user)
        return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.HomepageSlidersSerializer})
    @action(methods=['get'], detail=False, url_path='sliders', url_name='sliders')
    def sliders(self, request):
        queryset = Slider.objects.all()
        serializer = serializers.HomepageSlidersSerializer(queryset, many=True, context={'request': request})
        page = self.paginate_queryset(serializer.data)
        if page:
            return self.get_paginated_response(page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.HomepageTollsSerializer})
    @action(methods=['get'], detail=False, url_path='tolls', url_name='tolls')
    def tolls(self, request):
        return Response({
            'taxi': constance_lib.taxi,
            'delivery_service': constance_lib.delivery_serv,
            'booking': constance_lib.booking,
        }, status=status.HTTP_200_OK)
