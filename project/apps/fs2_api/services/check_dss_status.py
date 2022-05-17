import logging

from django.utils import cache

from rest_framework.exceptions import ValidationError

from ._get_actual_api import get_actual_fs2_api

logger = logging.getLogger()


def check_dss_status(data, user):
    api = get_actual_fs2_api(user)
    if not api.is_alive():
        raise ValidationError({
            'detail': 'Время жизни сессии истекло',
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

    check_dss_uri = action_obj['action_sign_status_uri']

    url = f'https://api.pharmstd.ru{check_dss_uri}'
    response, status_code = api.json_request('get', url)
    return response
