import logging

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from apps.helpers import viewsets
from apps.news.models import (
    PharmMarketArticle, CompanyArticle, PersonnelChange, Birthday, Tag,
)
from .loaders.birthdays import BirthdaySerializer
from .loaders.personnel_changes import PersonnelChangeSerializer
from . import serializers
from . import filters

logger = logging.getLogger('django')


class CompanyNewsViewSet(viewsets.ExtendedModelViewSet):
    queryset = CompanyArticle.objects.all().order_by('-publish_date')
    serializer_class = serializers.CompanySerializer
    serializer_class_map = {
        'birthdays': BirthdaySerializer,
        'personnel_changes': PersonnelChangeSerializer,
    }
    permission_classes = (permissions.AllowAny,)
    filterset_class = filters.CompanyArticleFilterSet
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('title', 'description',)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.TagSerializer})
    @action(methods=['get'], detail=False, url_path='tags', url_name='tags')
    def tags(self, request):
        qs = Tag.objects.all()
        serializer = serializers.TagSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(responses={status.HTTP_200_OK: BirthdaySerializer})
    @action(methods=['get'], detail=False, url_path='birthdays', url_name='birthdays')
    def birthdays(self, request):
        qs = Birthday.objects.all()
        serializer = BirthdaySerializer(qs, many=True, context={'request': request})
        page = self.paginate_queryset(serializer.data)
        if page:
            return self.get_paginated_response(page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: PersonnelChangeSerializer})
    @action(methods=['get'], detail=False, url_path='personnel-changes', url_name='personnel-changes')
    def personnel_changes(self, request):
        qs = PersonnelChange.objects.all()
        serializer = PersonnelChangeSerializer(qs, many=True, context={'request': request})
        page = self.paginate_queryset(serializer.data)
        if page:
            return self.get_paginated_response(page)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PharmNewsViewSet(viewsets.ExtendedModelViewSet):
    queryset = PharmMarketArticle.objects.all().order_by('-publish_date')
    serializer_class = serializers.PharmMarketSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_class = filters.PharmMarketArticleFilterSet
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('title', 'description',)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.TagSerializer})
    @action(methods=['get'], detail=False, url_path='tags', url_name='tags')
    def tags(self, request):
        qs = Tag.objects.all()
        serializer = serializers.TagSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)
