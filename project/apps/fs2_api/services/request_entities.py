import logging
from uuid import uuid4

from django.core.cache import cache

from rest_framework.exceptions import ValidationError

from ._get_actual_api import get_actual_fs2_api

logger = logging.getLogger()


def get_default_actions(record):
    """
    Отобрать действия по-умолчанию у документов в списке
    документов, сохранить в кэш.
    """
    default_actions = []

    for def_action in record.get('defaultactions', []):
        def_action_id = uuid4()
        def_action_obj = {
            'id': def_action_id,
            'caption': def_action['caption'],
            'act_execute_uri': def_action['actexecuteuri'],
        }
        cache.set(def_action_id, def_action_obj)
        def_action_obj.pop('act_execute_uri')
        default_actions.append(def_action_obj)

    return default_actions


def get_all_entities(user, query_params=None, is_documents=True):
    """
    Получить список всех сущностей. Идет обращение к апи фармСЭДа, запрос и
    загрузка документов, сбор данных документов по формату сериализатора, также
    работа с кэшем: занести в него инфу о документе и действиях по-умолчанию. По
    флагу решить, какой тип сущностей необходимо загрузить - доки/задачи.
    В запросе на список документов так же необходимо сформировать новую сессию.
    """
    api = get_actual_fs2_api(user, need_new_session=True)

    # Поскольку документы и задачи по сути своей одни и
    # те же сущности, тут просто решаем, что вызвать по флагу
    documents = api.documents() if is_documents else api.tasks()

    documents_list = []
    for record in documents:
        # Каждый объект record (документ) сохранить целиком в кеше
        record_id = uuid4()
        cache.set(record_id, record, timeout=60*60*3)
        default_actions = get_default_actions(record)

        req_attention = record.get('readdate', None)
        try:
            documents_list.append({
                'id': record_id,
                'requires_attention': False if req_attention else True,
                'name': record['name'],
                'human_name': record['caption'] if record['caption'] else None,
                'date': record['indate'],
                'date_deadline': record['deadline'],
                'status': record['state'],
                'source': 'ФС2',
                'attachment_count': 0,  # TODO узнать нужно ли это тут
                'user_responsible': record['owner'],
                'type': 'Активные',
                'default_actions': default_actions,
            })
        except Exception as exc:
            error_message = {
                'detail': 'Возникла ошибка при присвоении значений объекту документа',
                'source': str(exc),
                'status': 400,
            }
            logger.error(error_message)
            raise ValidationError(error_message)

    # Найти/отфильтровать нужные документы, если есть search параметр
    if query_params and 'search' in query_params:
        searched_list = list()
        for dict_ in documents_list:
            # Ищем регистронезависимо
            name_contains = dict_['name'].lower().find(query_params['search'].lower())
            human_name_contains = dict_['human_name'].lower().find(query_params['search'].lower())
            if name_contains != -1 or human_name_contains != -1:
                searched_list.append(dict_)
        return searched_list

    return documents_list
