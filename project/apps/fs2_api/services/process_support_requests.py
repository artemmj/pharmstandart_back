import os

from django.conf import settings
from django.http import HttpRequest

from api.v1.data_center.serializers import (
    InitSupportRequestSerializer, SendSupportRequestSerializer, AddAttachToSupportRequestSerializer,
)
from ._get_actual_api import get_actual_fs2_api


def init_support_request(request: HttpRequest) -> dict:
    api = get_actual_fs2_api(request.user, need_new_session=True)
    datas = api.init_support_request()[0]

    datas.pop('classname', None)
    datas.pop('addattachuri', None)

    datas['app_id'] = api.app_id
    serializer = InitSupportRequestSerializer(data=datas)
    serializer.is_valid(raise_exception=True)

    directions = list()  # направления
    request_types = list()  # типы заявок
    sd = serializer.data.copy()

    support_types = sd.pop('SupportTypes', None)
    for sp in support_types:
        if sp['parentid'] and sp['parentid'] != '':
            request_types.append(sp)
        else:
            directions.append(sp)
    sd['directions'] = directions
    sd['request_types'] = request_types
    return sd


def send_support_request(request: HttpRequest) -> dict:
    post_data = request.data.copy()
    serializer = SendSupportRequestSerializer(data=post_data)
    serializer.is_valid(raise_exception=True)
    valid_data = serializer.data.copy()
    valid_data['classname'] = 'SupportRequestCommit'

    # На стороне фс2 происходит задваивание комментария. Скорее всего из-за
    # того, что мобилки шлют один текст и в text и в subject. Очистить одно.
    # TODO Уточнить, что нужно отправлять в text а что в subject.
    if valid_data['subject']:
        valid_data['subject'] = ''

    api = get_actual_fs2_api(request.user, need_new_session=False)
    api.app_id = valid_data.pop('app_id', None)
    response = api.send_support_request(valid_data)
    return response


def add_attach_to_support_request(request: HttpRequest) -> None:
    """ Логика обработки валидированных сырых данных по
    отправке файла в создании заявки в ЦОД.
    """
    serializer = AddAttachToSupportRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    valid_data = serializer.data.copy()

    if not os.path.exists(f'{settings.MEDIA_URL}support_attachs'):
        os.mkdir(f'{settings.MEDIA_URL}support_attachs')

    file = request.FILES['file']
    file_dest = f'{settings.MEDIA_URL}support_attachs/{file.name}'
    dest = open(file_dest, 'wb+')
    for chunk in file.chunks():
        dest.write(chunk)
    dest.close()

    api = get_actual_fs2_api(request.user, need_new_session=False)
    api.app_id = valid_data.pop('app_id', None)
    valid_data['app_id'] = api.app_id
    api.add_attach_support_request(valid_data, file_dest)
    return
