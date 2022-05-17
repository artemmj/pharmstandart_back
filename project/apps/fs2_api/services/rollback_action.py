import logging

from django.core.cache import cache

from rest_framework.exceptions import ValidationError

from ._get_actual_api import get_actual_fs2_api

logger = logging.getLogger()


def rollback_action(data, user):
    """
    Выполнить роллбэк, откатить выполнение действия.
    """
    api = get_actual_fs2_api(user)
    if not api.is_alive():
        raise ValidationError({
            'detail': 'Время жизни сессии истекл',
            'source': 'session_expired',
            'status': 400,
        })

    action_obj_cache = cache.get(data['action_id'])
    if not action_obj_cache:
        error_message = {
            'detail': 'Не найден документ с таким action_id',
            'source': data['action_id'],
            'status': 400,
        }
        logger.error(error_message)
        raise ValidationError(error_message)

    action_rollback_uri = action_obj_cache['action_rollback_uri']
    url = f'https://api.pharmstd.ru{action_rollback_uri}'
    response = api.request('get', url)

    # TODO В этом месте могут вылезти проблемы, добавить проверки корректности запроса

    return {
        'status_code': response.status_code,
        'result': response.content,
    }
