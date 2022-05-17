from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from . import serializers
from . import services


class ELibraryApiView(GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        query_serializer=serializers.ELibListQuerySerializer,
        responses={status.HTTP_200_OK: serializers.ELibSearchResponseSerializer(many=True)}
    )
    def list(self, request):
        query_serializer = serializers.ELibListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        return Response(services.get_all_documents(request, query_serializer.data))

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.ELibRetrieveSerializer})
    def retrieve(self, request, pk):
        return Response(services.retrieve_document(request, pk))

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.ELibInternStatusSerializer(many=True)})
    @action(methods=['get'], detail=False, url_path='statuses', url_name='statuses')
    def statuses(self, request):
        return Response(services.get_elib_statuses(request))

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.ELibInternRubricSerializer(many=True)})
    @action(methods=['get'], detail=False, url_path='rubrics', url_name='rubrics')
    def rubrics(self, request):
        return Response(services.get_elib_rubrics(request))

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.ELibInternStatusSerializer(many=True)})
    @action(methods=['get'], detail=False, url_path='categories', url_name='categories')
    def categories(self, request):
        return Response(services.get_elib_categories(request))

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: serializers.ELibSearchResponseSerializer(many=True)},
        request_body=serializers.ELibSearchRequestSerializer)
    @action(methods=['post'], detail=False, url_path='search', url_name='search')
    def search(self, request):
        serializer = serializers.ELibSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(services.prepare_datas_for_elib_search(request, serializer.data))
