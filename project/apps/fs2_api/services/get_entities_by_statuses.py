
def get_statuses_from_documents(documents):
    ''' Вернуть список возможных для сущности (док/задача) статусов. '''
    statuses = set()
    for doc in documents:
        statuses.add(doc['status'].strip())
    return {'result': statuses}


def get_filtered_documents_by_status(documents, status):
    ''' Отфильтровать список сущностей по переданному статусу. '''
    result_list = []
    for doc in documents:
        if doc['status'].strip() == status:
            result_list.append(doc)
    return result_list
