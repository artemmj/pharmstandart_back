import logging

from django.core.cache import cache

from rest_framework.exceptions import ValidationError

from ._get_actual_api import get_actual_fs2_api

logger = logging.getLogger()


def commit_action(data, user):
    """
    Выполнить коммит действия. Сначала из кэша необходимо достать объект
    содержащий необходимые uri's. Далее необходимо проверить соответствие
    флагов и параметров пост запроса.
    """
    api = get_actual_fs2_api(user)
    if not api.is_alive():
        raise ValidationError({
            'detail': 'Время жизни сессии истекло',
            'source': 'session_expired',
            'status': 400,
        })

    action_id = data.pop('action_id')
    action_obj_cache = cache.get(action_id)
    if not action_obj_cache:
        error_message = {
            'detail': 'Не найден документ с таким action_id',
            'source': action_id,
            'status': 400,
        }
        logger.error(error_message)
        raise ValidationError(error_message)

    action_obj = action_obj_cache['action_object']
    action_commit_uri = action_obj_cache['action_commit_uri']

    if action_obj['need_dead_line'] is True and 'deadline' not in data:
        raise ValidationError({
            'detail': 'Требуется параметр при need_dead_line == True',
            'source': 'deadline',
            'status': 400,
        })

    if action_obj['need_comment'] is True and 'comment' not in data:
        raise ValidationError({
            'detail': 'Требуется параметр при need_comment == True',
            'source': 'comment',
            'status': 400,
        })

    if action_obj['sign_confirm_type'] == 'cntSMS' and 'sign_confirm_code' not in data:
        raise ValidationError({
            'detail': 'Требуется параметр при sign_confirm_type == cntSMS',
            'source': 'sign_confirm_code',
            'status': 400,
        })

    # Неободимо привести все имеющиеся guid's к верхнему
    # регистру и заключить в фигурные скобки
    if 'acceptors' in data:
        for acc in data['acceptors']:
            acc['userid'] = f'{{{acc["userid"].upper()}}}'

    headers = {'Content-type': 'application/json'}
    url = 'https://api.pharmstd.ru' + action_commit_uri
    response, status_code = api.json_request('post', url, headers=headers, json=data)

    # TODO В этом месте могут вылезти проблемы, добавить проверки корректности запроса

    return {
        'status_code': status_code,
        'result': response,
    }
