import os
import uuid
import logging

from django.conf import settings
from django.core.cache import cache
from django.http.request import HttpRequest
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer

from apps.fs2_api.portal_proxy import PortalApiProxy
from . import serializers

logger = logging.getLogger('django')


def process_raw_data(serializer: Serializer, result: dict) -> list:
    """ Вспомогательная функция, делает общие вещи для функций ниже. """
    serializer.is_valid(raise_exception=True)
    if serializer.data['s_error']:
        error_message = {
            'detail': 'Ошибка апи портала при получении списка статусов для электронной библиотеки',
            'source': serializer.data['message'],
            'status': 401,
            's_error': serializer.data['s_error'],
        }
        logger.error(error_message)
        raise ValidationError(error_message)
    return serializer.data['Items']


def get_elib_statuses(request: HttpRequest) -> dict:
    """ Обработка инфы по статусам elib. """
    api_portal = PortalApiProxy(login=request.user.email, password=request.user.get_enc_pass)
    result = api_portal.get_elib_statuses()
    serializer = serializers.ELibExternStatusSerializer(data=result)
    return process_raw_data(serializer, result)


def get_elib_rubrics(request: HttpRequest) -> dict:
    """ Обработка инфы по рубрикам elib. """
    api_portal = PortalApiProxy(login=request.user.email, password=request.user.get_enc_pass)
    result = api_portal.get_elib_rubrics()
    serializer = serializers.ELibExternRubricSerializer(data=result)
    return process_raw_data(serializer, result)


def get_elib_categories(request: HttpRequest) -> dict:
    """ Обработка инфы по категориям elib. """
    api_portal = PortalApiProxy(login=request.user.email, password=request.user.get_enc_pass)
    result = api_portal.get_elib_categories()
    serializer = serializers.ELibExternCategorySerializer(data=result)
    return process_raw_data(serializer, result)


def cache_documents(serializer_data: list) -> list:
    ''' Кэширует документы.
    '''
    for row in serializer_data:
        # Положить каждый документ в кэш, для детального вида, время небольшое
        row['Id'] = uuid.uuid4()
        cache.set(row['Id'], row, timeout=60*60)
    return serializer_data


def get_all_documents(request: HttpRequest, query_params: dict) -> list:
    ''' Вернуть все документы для главного экрана электронной
    библиотеки. Берем по всем доступным категориям.
    '''
    api_portal = PortalApiProxy(login=request.user.email, password=request.user.get_enc_pass)
    resp_statuses = api_portal.get_elib_statuses()
    statuses_serializer = serializers.ELibExternStatusSerializer(data=resp_statuses)
    statuses_serializer.is_valid(raise_exception=True)
    if 'status' in query_params:
        statuses_list = [query_params['status']]
    else:
        statuses_list = [item_data['Name'] for item_data in statuses_serializer.data['Items']]

    resp_docs = api_portal.search_elib({'Status': statuses_list})
    docs_serializer = serializers.ELibRetrieveSerializer(data=resp_docs['Result'], many=True)
    docs_serializer.is_valid(raise_exception=True)
    cached = cache_documents(docs_serializer.data)
    [cah.pop('DocumentPath') for cah in cached]  # для list'a убрать DocumentPath
    return cached


def prepare_datas_for_elib_search(request: HttpRequest, serializer_data: dict) -> list:
    """
    Функция принимает объект HttpRequest и валидированные данные
    этого пост-запроса, анализирует состав, формирует пакет и шлет
    в апи портала. Ответ апи портала валидируется и возвращается.
    """
    if not serializer_data:
        # Требование: возможность поиска вообще без параметров :) Для
        # этого использую метод для отображения списка документов:
        # просто ищем по всем возможным статусам.
        return get_all_documents(request, request.query_params)

    api_portal = PortalApiProxy(login=request.user.email, password=request.user.get_enc_pass)
    resp_docs = api_portal.search_elib(serializer_data)
    docs_serializer = serializers.ELibSearchResponseWithDocPathSerializer(data=resp_docs['Result'], many=True)
    docs_serializer.is_valid(raise_exception=True)
    return cache_documents(docs_serializer.data)


def retrieve_document(request: HttpRequest, pk: str):
    ''' Получить детальный вид документа. Выносить пришлось,
    чтобы вынести загрузку файла в детальный вид.
    '''
    if not os.path.exists(settings.MEDIA_ROOT + '/elibrary'):
        os.makedirs(settings.MEDIA_ROOT + '/elibrary')

    document = cache.get(pk)
    if not document:
        raise ValidationError({
            'detail': 'Не найден документ с таким id',
            'source': pk,
            'status': 400,
        })

    uncorrect_path = document.pop('DocumentPath', None)
    if uncorrect_path:
        # Сохранить документ если есть, вернуть нормальный путь до него
        portal_api = PortalApiProxy(
            request.user.email.split('@')[0],
            request.user.get_enc_pass
        )
        response = portal_api.request('get', uncorrect_path, stream=True)

        filename = uncorrect_path.split('/')[-1]
        file_dest = settings.MEDIA_ROOT + f'/elibrary/{filename}'
        with open(file_dest, 'wb') as fd:
            for chunk in response.iter_content(128):
                fd.write(chunk)
        document['DocumentPath'] = request.build_absolute_uri(file_dest)
    else:
        document['DocumentPath'] = None

    return document
