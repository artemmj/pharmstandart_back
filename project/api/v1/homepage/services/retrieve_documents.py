from uuid import uuid4

from django.core.cache import cache

from apps.fs2_api.api_proxy import Fs2ApiProxy


def retrieve_documents(user):
    ''' Получить документы для домашнего экрана. Необходимо разделить документы
    по статусам, вернуть сортированными.
    '''
    fs2_api = Fs2ApiProxy(login=user.email, password=user.get_enc_pass)
    documents = fs2_api.documents()

    # Отобрать типы документов количество каждого
    status_names = {}
    for record in documents:
        if record['state'].strip() in status_names.keys():
            status_names[record['state'].strip()] += 1
        else:
            status_names[record['state'].strip()] = 1

    result = []
    for key, value in status_names.items():
        result.append({'status_name': key, 'status_count': value, 'documents': []})
    # Тут первичная структура данных, осталось добавить сами документы

    for doc in documents:
        # Каждый объект record (документ) сохранить целиком в кеше
        record_id = uuid4()
        cache.set(record_id, doc, timeout=60*60*3)

        for res_obj in result:
            # Если тип документа в списке всех совпадает с каким-то
            # в результирующем наборе данных - добавить его в список
            if doc['state'].strip() == res_obj['status_name']:

                def_actions = []
                if 'defaultactions' in doc:
                    for action in doc['defaultactions']:
                        action_id = uuid4()

                        def_actions.append({  # действие в результат
                            'id': action_id,
                            'caption': action['caption'],
                            'status': action['status'],
                        })

                        cache.set(  # действие (ури) в кэш
                            action_id,
                            {'act_execute_uri': action['actexecuteuri']},
                            timeout=60*60*3
                        )

                req_attention = doc.get('readdate', None)
                res_obj['documents'].append({
                    'id': record_id,
                    'requires_attention': False if req_attention else True,
                    'name': f'{doc["name"]} / {doc["caption"]}',
                    'amount': doc['amount'],
                    'date_deadline': doc['deadline'],
                    'source': 'ФС2',
                    'default_actions': def_actions,
                })
            else:
                continue

    return result
