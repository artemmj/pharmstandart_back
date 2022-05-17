import logging

from constance import config as constance_lib
from rest_framework import status
from rest_framework.exceptions import ValidationError

logger = logging.getLogger()


class BaseApiProxy:
    API_URL = 'https://api.pharmstd.ru'
    # Название БД изменится, пока что тестовое.
    DB_NAME = constance_lib.working_fs2_db
    # Роут для старта приложения на стороне фармы.
    APP_START_URI = '/appstart?callback=none&clinfo=mobapp'

    login = None
    password = None

    app_id = None

    db_id = None
    db_open_uri = None

    inbox_uri = None
    outbox_uri = None
    my_staff_uri = None
    errands_uri = None
    new_ent_dlg_uri = None
    workspace_uri = None

    def request(self, method, url, **kwargs):
        ''' Выполняет простой запрос по существующей сессии '''
        try:
            response = getattr(self.session, method)(url, **kwargs)
            return response
        except Exception as exc:
            error_message = {
                'detail': 'Ошибка выполнения запроса',
                'source': url,
                'exc': str(exc)}
            logger.error(error_message)
            raise ValidationError(error_message)

    def json_request(self, method, url, **kwargs):
        ''' Выполяет запрос по аутентифицированному
            (не факт) пользователю в сессии.
            - method - метод
            - url - url запроса
            - return tuple: json, status_code
        '''
        error_message = None
        try:
            response = getattr(self.session, method)(url, **kwargs)
            if response.status_code == status.HTTP_200_OK:
                json_response = response.json()
            else:
                content = str(response.content.decode('utf-8'))
                error_message = {
                    'detail': f'Ошибка апи фс2/портала: {content}',
                    'source': url,
                }
                if response.status_code == 499:
                    error_message['status'] = '400'
                else:
                    error_message['status'] = response.status_code,
        except Exception as exc:
            error_message = {
                'detail': 'Возникла ошибка при запросе',
                'source': url,
                'status': 400,
                'type': type(exc),
                'exc': str(exc),
            }

        if error_message:
            logger.error(error_message)
            raise ValidationError(error_message)

        return json_response, response.status_code

    def is_alive(self):
        """ Проверить статус жизни сессии. """
        response = self.request('get', f'{self.API_URL}/amalive?appid={self.app_id}')
        return True if response.status_code == status.HTTP_200_OK else False
