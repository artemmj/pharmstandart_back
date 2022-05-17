import logging
from uuid import uuid4

from django.core.cache import cache

from rest_framework.exceptions import ValidationError

from ._get_actual_api import get_actual_fs2_api

logger = logging.getLogger('django')

API_URL = 'https://api.pharmstd.ru'


def get_signs(entity_obj):
    """
    Вытащить объекты signs (лист согласования/подписания)
    по переданному объекту сущности/entity.
    """
    signs = entity_obj.get('signs', {})
    signs_items = signs.get('items', []) if signs else []
    return_signs_items = []

    for item in signs_items:
        return_signs_items.append({
            'id': uuid4(),
            'sign_user_caption': item['signusercaption'],
            'sign_name': item['signname'],
            'sign_datetime': item['signdt'],
        })

    return return_signs_items


def get_attachs(entity_obj):
    """
    Вытащить объекты attach (вложения) и их
    количество по переданному объекту сущности.
    """
    attachs = entity_obj.get('attachs', {})
    attachs_items = attachs.get('items', []) if attachs else []
    attachs_count = attachs.get('count') if attachs else 0
    return_attachs_items = []

    for item in attachs_items:
        return_attachs_items.append({
            'id': uuid4(),
            'file': f'{API_URL}{item["filegeturi"]}',
            'filename': item['filename'],
            'date': item['attachdate'],
        })

    return return_attachs_items, attachs_count


def get_default_red_green_actions(entity_obj):
    """
    Вытащить объекты default_action (действия по-умолчанию).
    """
    def_actions_obj = entity_obj.get('defaultactions', [])
    def_actions = def_actions_obj.get('items', []) if def_actions_obj else []

    green_actions = list()
    red_actions = list()

    for action in def_actions:
        if action['visible'] and action['enabled'] and action['status'] in ['asGreen', 'asRed']:
            action_id = uuid4()
            cache.set(action_id, {'act_execute_uri': action['actexecuteuri']}, timeout=60*60*3)
            if action['status'] == 'asGreen':
                green_actions.append({
                    'id': action_id,
                    'action_type': action['actiontype'],
                    'caption': action['caption'],
                    'status': action['status'],
                })
            elif action['status'] == 'asRed':
                red_actions.append({
                    'id': action_id,
                    'action_type': action['actiontype'],
                    'caption': action['caption'],
                    'status': action['status'],
                })

    return green_actions, red_actions


def get_other_actions(entity_obj):
    """
    Вытащить объекты actions (все действия над документом).
    """
    std_actions_obj = entity_obj.get('stdactions', {})
    std_actions = std_actions_obj.get('items', []) if std_actions_obj else []
    return_actions = list()

    disabled_actions = [
        'atSimple', 'atPrint', 'atCreate', 'atOpen', 'atTask', 'atEdit',
        'atSystem', 'atCreateSubTask', 'atTrash', 'atSimple', 'atPrint',
        'atRecordSet',
    ]

    for action in std_actions:  # TODO пока вручную убираем ненужные действия
        if action['actiontype'] not in disabled_actions:
            std_action_id = uuid4()
            cache.set(std_action_id, {'act_execute_uri': action['actexecuteuri']}, timeout=60*60*3)
            if action['visible'] and action['enabled']:
                return_actions.append({
                    'id': std_action_id,
                    'action_type': action['actiontype'],
                    'caption': action['caption'],
                    'status': action['status'],
                })

    addon_actions_obj = entity_obj.get('addonactions', {})
    addon_actions = addon_actions_obj.get('items', []) if addon_actions_obj else []

    for action in addon_actions:  # TODO пока вручную убираем ненужные действия
        if action['actiontype'] not in disabled_actions:
            addon_action_id = uuid4()
            cache.set(addon_action_id, {'act_execute_uri': action['actexecuteuri']}, timeout=60*60*3)
            if action['visible'] and action['enabled']:
                return_actions.append({
                    'id': addon_action_id,
                    'action_type': action['actiontype'],
                    'caption': action['caption'],
                    'status': action['status'],
                })

    return sorted(return_actions, key=lambda x: x['status'])


def get_comments(entity_obj):
    """
    Вытащить comments (комментарии) из переданной сущности.
    """
    pharm_comments_obj = entity_obj.get('comments')
    return_comments = []

    if pharm_comments_obj['count'] > 0:
        comments = pharm_comments_obj.get('items', [])
        for comment in comments:
            # Верхний уровень, без акцептантов
            comments_data = {
                'id': comment['id'],
                'comment_text': comment['commenttext'],
                'motion_type': comment['motiontype'],
                'event_name': comment['eventname'],
                'for_user_caption': comment['forusercaption'],
                'for_user_name': comment['forusername'],
                'for_user_id': comment['foruserid'],
                'author_caption': comment['authorcaption'],
                'author_name': comment['authorname'],
                'author_id': comment['authorid'],
                'datetime': comment['datetime'],
                'actions': [],
                'attachs': [],
                'acceptors': [],
            }
            # Набрать акцептантов
            acceptors_data = comment.get('acceptors', {})
            if acceptors_data and 'count' in acceptors_data and acceptors_data['count'] > 0:
                acceptors_items = acceptors_data.get('items', [])
                for acceptor in acceptors_items:
                    comments_data['acceptors'].append({
                        'class_name': acceptor['classname'],
                        'id': acceptor['id'],
                        'user_id': acceptor['userid'],
                        'user_caption': acceptor['usercaption'],
                        'username': acceptor['username'],
                        'user_state': acceptor['userstate'],
                        'origin': acceptor['origin'],
                        'acceptor_type': acceptor['acceptortype'],
                    })
            # Набрать аттачи
            attachs_data = comment.get('attachs', {})
            if attachs_data and 'count' in attachs_data and attachs_data['count'] > 0:
                attachs_items = attachs_data.get('items', [])
                for attach in attachs_items:
                    comments_data['attachs'].append({
                        'class_name': attach['classname'],
                        'id': attach['id'],
                        'field_caption': attach['fieldcaption'],
                        'field_name': attach['fieldname'],
                        'field_attach': attach['fieldattach'],
                        'file': f'{API_URL}{attach["filegeturi"]}',
                        'filename': attach['filename'],
                        'caption': attach['caption'],
                        'crc32': attach['crc32'],
                        'attach_date': attach['attachdate'],
                        'file_size': attach['filesize'],
                        'file_type': attach['filetype'],
                        'attach_user_caption': attach['attachusercaption'],
                    })
            # Набрать действия над комментариями, сохранить в кеше
            actions_data = comment.get('actions', {})
            if actions_data and 'count' in actions_data and actions_data['count'] > 0:
                action_items = actions_data.get('items', [])
                for action in action_items:
                    action_id = uuid4()

                    cache.set(action_id, {'act_execute_uri': action['actexecuteuri']}, timeout=60*60*3)

                    comments_data['actions'].append({
                        'id': action_id,
                        'caption': action['caption'],
                        'action_type': action['actiontype'],
                        'is_default': action['isdefault'],
                        'status': action['status'],
                        # 'actexecuteuri': action['actexecuteuri'],
                    })

            return_comments.append(comments_data)

    return return_comments


def get_tabs(entity_obj, fs2_api):
    """
    Вытащить tabs (динамические вкладки в подробном виде документа).
    """
    tabs_obj = entity_obj.get('tabs')
    return_tabs = []

    if tabs_obj['count'] > 0:
        tabs_list = tabs_obj.get('items', [])
        # Для каждой вкладки необходимо решить, какая она, и создать ее
        for tab in tabs_list:
            tab_obj = {'caption': tab['caption'], 'data': {}, 'content': []}
            childcontrols = tab.get('childcontrols', {})
            # Информационная вкладка - список, лист данных
            if childcontrols and childcontrols['count'] > 0:
                tab_obj['type'] = 'INFO'
                childcontrols_items = childcontrols.get('items', [])
                for row in childcontrols_items:
                    tab_obj['content'].append({
                        'id': row['id'],
                        'caption': row['caption'],
                        'control_type': row['controltype'],
                        'text': row['text'],
                        'warn_hint': row['warnhint'],
                        'choise_type': row['choisetype'],
                        'data_type': row['datatype'] if 'datatype' in row else None,
                        # NOTE расширится в дальнейшем
                    })
                return_tabs.append(tab_obj)
                continue
            # НЕинформационная, таблица либо файл
            else:
                control = tab.get('control', {})
                if 'datatype' in control:
                    # Табличная
                    if control['datatype'] == 'DTCOMPOSITELIST':
                        tab_obj['type'] = 'TABULAR'
                        recordset_uri = f'https://api.pharmstd.ru{control["recordseturi"]}'
                        response, status_code = fs2_api.json_request('get', recordset_uri)
                        records = response.get('records', list)
                        columns_info = response.get('columns', dict).get('items', list)

                        col_info_dict = {item['fieldname']: item['caption'] for item in columns_info}
                        for record in records:
                            for key in col_info_dict.keys():
                                record[col_info_dict[key]] = record.pop(key)

                        tab_obj['content'] = records
                        return_tabs.append(tab_obj)
                        continue
                    # Файловая
                    elif control['datatype'] == 'DTFILE':
                        tab_obj['type'] = 'FILE'

                        tab_obj['data'] = {
                            'id': control['id'],
                            'caption': control['caption'],
                            'control_type': control['controltype'],
                            'text': control['text'],
                            'warn_hint': control['warnhint'],
                            'choise_type': control['choisetype'],
                            'data_type': control['datatype'] if 'datatype' in control else None,
                            'filegeturi': f'{API_URL}{control["filegeturi"]}' if 'filegeturi' in control else None,
                            'fileputuri': f'{API_URL}{control["fileputuri"]}' if 'fileputuri' in control else None,
                        }
                        return_tabs.append(tab_obj)
                        continue

    return return_tabs


def get_default_actions(entity_obj):
    """
    Вытащить объекты default_action (действия по-умолчанию).
    """
    def_actions_obj = entity_obj.get('defaultactions', [])
    def_actions = def_actions_obj.get('items', []) if def_actions_obj else []
    return_default_actions = []

    for action in def_actions:
        action_id = uuid4()
        cache.set(action_id, {'act_execute_uri': action['actexecuteuri']}, timeout=60*60*3)
        return_default_actions.append({
            'id': action_id,
            'caption': action['caption'],
            'status': action['status'],
        })

    return return_default_actions


def get_actions(entity_obj):
    """
    Вытащить объекты actions (все действия над документом).
    """
    std_actions_obj = entity_obj.get('stdactions', {})
    std_actions = std_actions_obj.get('items', []) if std_actions_obj else []
    return_actions = list()

    disabled_actions = [
        'atSimple', 'atPrint', 'atCreate', 'atOpen', 'atTask', 'atEdit',
        'atSystem', 'atCreateSubTask', 'atTrash', 'atSimple', 'atPrint',
        'atRecordSet',
    ]

    for action in std_actions:  # TODO пока вручную убираем ненужные действия
        if action['actiontype'] not in disabled_actions:
            std_action_id = uuid4()
            cache.set(std_action_id, {'act_execute_uri': action['actexecuteuri']}, timeout=60*60*3)
            if action['visible'] and action['enabled']:
                return_actions.append({
                    'id': std_action_id,
                    'action_type': action['actiontype'],
                    'caption': action['caption'],
                    'status': action['status'],
                })

    addon_actions_obj = entity_obj.get('addonactions', {})
    addon_actions = addon_actions_obj.get('items', []) if addon_actions_obj else []

    for action in addon_actions:  # TODO пока вручную убираем ненужные действия
        if action['actiontype'] not in disabled_actions:
            addon_action_id = uuid4()
            cache.set(addon_action_id, {'act_execute_uri': action['actexecuteuri']}, timeout=60*60*3)
            if action['visible'] and action['enabled']:
                return_actions.append({
                    'id': addon_action_id,
                    'action_type': action['actiontype'],
                    'caption': action['caption'],
                    'status': action['status'],
                })

    return sorted(return_actions, key=lambda x: x['status'])


def get_detailed_entity(user, doc_uuid):
    """ Получить детальный вид документа/задачи. Выполняется
    открытие/подключение по данным пользователя (возможно, нет смысла), запрос
    на entshowuri (детальный вид от фармСЭД), и разбор/обработка пришедших
    данных в соответствии с сериализаторами.
    """
    api = get_actual_fs2_api(user)

    record = cache.get(doc_uuid)
    if not record:
        raise ValidationError({
            'detail': 'Не удалось найти документ с таким айди',
            'source': doc_uuid,
            'status': 400,
        })

    entshow_uri = f'{API_URL}{record["entshowuri"]}'
    entity_obj, _ = api.json_request('get', entshow_uri)

    # Лист согласования
    signs_items = get_signs(entity_obj)
    # Вложения
    attachs_items, attachs_count = get_attachs(entity_obj)
    # Комментарии
    comments = get_comments(entity_obj)
    # Динамические табы, вкладки
    tabs = get_tabs(entity_obj, api)
    # Действия основые, положительные и отрицательные
    green_actions, red_actions = get_default_red_green_actions(entity_obj)
    # Другие действия
    other_actions = get_other_actions(entity_obj)

    return_default_actions = get_default_actions(entity_obj)
    return_actions = get_actions(entity_obj)

    try:
        return {
            'id': doc_uuid,
            'name': record['name'],
            'human_name': record['caption'] if record['caption'] else None,
            'date': record['indate'][:10] if record['indate'] else None,
            'date_deadline': record['deadline'][:10] if record['deadline'] else None,
            'status': record['state'],
            'source': 'ФС2',
            'signatory': record['owner'],
            'delivery_method': '',
            'organisation': 'ООО Фармстандарт-Плазма',
            'attachment_count': attachs_count,
            'user_responsible': record['owner'],
            'type': 'Активные',
            'in_answer_to': '24798-5335',
            'mail': '',
            'attachs': attachs_items,
            'signs': signs_items,
            'green_actions': green_actions,
            'red_actions': red_actions,
            'other_actions': other_actions,
            'comments': comments,
            'tabs': tabs,
            # TODO Убрать старые действия после мобилок
            'default_actions': return_default_actions,
            'actions': return_actions,
        }
    except Exception as exc:
        error_message = {
            'detail': 'Возникла ошибка при присвоении данных объекту документа',
            'source': str(exc),
            'status': 400,
        }
        logger.error(error_message)
        raise ValidationError(error_message)
