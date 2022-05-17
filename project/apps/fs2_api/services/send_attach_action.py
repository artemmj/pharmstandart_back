import logging

from django.core.cache import cache

from rest_framework.exceptions import ValidationError

from ._get_actual_api import get_actual_fs2_api

logger = logging.getLogger()


def send_attach_action(data, user):
    api = get_actual_fs2_api(user)
    if not api.is_alive():
        raise ValidationError({
            'detail': 'Время жизни сессии истекл',
            'source': 'session_expired',
            'status': 400,
        })

    action_obj = cache.get(data['action_id'])
    if not action_obj:
        error_message = {
            'detail': 'Не найден документ с таким action_id',
            'source': data['action_id'],
            'status': 400,
        }
        logger.error(error_message)
        raise ValidationError(error_message)

    # TODO Необходимо учитывать эти поля в дальнейшем
    # can_modify_attachs = action_obj['can_modify_attachs']
    # need_attach = action_obj['need_attach']
    # max_attach_size = action_obj['max_attach_size']
    # max_attach_count = action_obj['max_attach_count']
    send_attach_uri = action_obj['action_add_attach_uri']
    filename = data['filepath'].split('/')[-1]
    file = open(data['filepath'], 'rb')
    url = f'https://api.pharmstd.ru{send_attach_uri}&fn={filename}'
    response, status_code = api.json_request('post', url, data=file)
    # TODO В этом месте могут вылезти проблемы, добавить проверки корректности запроса
    file.close()
    return {
        'status_code': status_code,
        'filegeturi': f'https://api.pharmstd.ru{response["filegeturi"]}',
    }
