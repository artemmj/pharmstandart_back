import logging
from uuid import uuid4

from django.core.cache import cache

from rest_framework.exceptions import ValidationError

from ._get_actual_api import get_actual_fs2_api

logger = logging.getLogger()


def get_visible_acceptors_types(act_execute_resp):
    """
    Отобрать типы акцептантов, которые необходимо отобразить, а так же
    заполнить соотвующие типы акцептантами по-умолчанию, если такие есть.
        atTo - получатели
        atCopy - кого уведомить
        atSigner - получатели TODO
    """
    visible_acceptor_types_obj = act_execute_resp.get('visibleacceptortypes', {})
    visible_acceptor_types = visible_acceptor_types_obj.get('items', []) if visible_acceptor_types_obj else []
    acceptors_types_obj = []

    for type in visible_acceptor_types:
        if type['acceptortype'] in ['atTo', 'atCopy']:
            acceptors_types_obj.append({
                'caption': type['caption'],
                'acceptor_type': type['acceptortype'],
                'acceptors': [],
            })

    default_acceptors_obj = act_execute_resp.get('defaultacceptors', {})
    default_acceptors = default_acceptors_obj.get('items', []) if default_acceptors_obj else []

    for type in acceptors_types_obj:
        for acceptor in default_acceptors:
            if type['acceptor_type'] == acceptor['acceptortype']:
                low_user_id = acceptor['userid'].lower()[1:-1]
                type['acceptors'].append({
                    'id': acceptor['id'],
                    'user_id': low_user_id,
                    'user_caption': acceptor['usercaption'],
                    'username': acceptor['username'],
                    'acceptor_type': acceptor['acceptortype'],
                })
                continue

    return acceptors_types_obj


def get_mru_acceptors(json_response):
    mruacceptors = json_response.get('mruacceptors', {})
    if mruacceptors['count'] < 1:
        return []
    else:
        result_list = list()
        items = mruacceptors.get('items', [])
        for acceptor in items:
            result_list.append({
                'id': acceptor['id'],
                'user_id': acceptor['userid'].lower()[1:-1],
                'user_caption': acceptor['usercaption'],
                'acceptor_type': acceptor['acceptortype'],
            })
        return result_list


def prepare_action(data, user):
    """
    Функция выполняет подготовку действия к выполнению. Прежде чем выполнить
    действие, на мк необходимо отобразить экран подготовки действия, в рамках
    которого можно, например, добавить вложение или акцептантов.
    """
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
            'detail': 'Документ с таким action_id не найден.',
            'source': data['action_id'],
            'status': 400,
        }
        logger.error(error_message)
        raise ValidationError(error_message)

    # В ответе на запрос act_execute_uri возвращается подробная
    # информация о действии и о возможных манипуляциях в рамках
    # действия, в т.ч. коммит или роллбэк действия
    url = f'https://api.pharmstd.ru{action_obj["act_execute_uri"]}'
    act_execute_resp, status_code = api.json_request('get', url)

    # Отобрать типы акцептантов, с акцептантами по-умолчанию
    acceptors_types_obj = get_visible_acceptors_types(act_execute_resp)

    # Отобрать часто используемых акцептантов
    mru_acceptors = get_mru_acceptors(act_execute_resp)

    # Сформировать итоговый объект
    action_id = uuid4()
    return_action_obj = {
        'id': action_id,
        'display_name': act_execute_resp['caption'],
        'owner': f'{user.first_name} {user.last_name}',
        'comment_label': act_execute_resp['commentlabel'],
        'default_comment': act_execute_resp['defaultcomment'],
        'can_modify_attachs': act_execute_resp['canmodifyattachs'],
        'default_dead_line': act_execute_resp['defaultdeadline'],
        'dead_line_visible': act_execute_resp['deadlinevisible'],
        'need_dead_line': act_execute_resp['needdeadline'],
        'dead_line_label': act_execute_resp['deadlinelabel'],
        'hint': act_execute_resp['hint'],
        'warn_hint': act_execute_resp['warnhint'],
        'caption': act_execute_resp['caption'],
        'need_attach': act_execute_resp['needattach'],
        'need_comment': act_execute_resp['needcomment'],
        'need_dialog': act_execute_resp['needdialog'],
        'max_attach_size': act_execute_resp['maxattachsize'],
        'max_attach_count': act_execute_resp['maxattachcount'],
        'sign_confirm_type': act_execute_resp['signconfirmtype'],
        'acceptors': acceptors_types_obj,
        'mru_acceptors': mru_acceptors,
    }

    # Сохранить в кэш необходимые uri's подготовки действия
    cache.set(
        action_id,
        {
            'action_object': return_action_obj,
            'action_commit_uri': act_execute_resp['actcommituri'],
            'action_rollback_uri': act_execute_resp['actrollbackuri'],
            'action_add_attach_uri': act_execute_resp['actaddattachuri'],
            'action_add_acceptor_uri': act_execute_resp['actaddacceptoruri'],
            'action_sign_status_uri': act_execute_resp['actsignstatusuri'],
        },
        timeout=60*60*3
    )

    return return_action_obj
