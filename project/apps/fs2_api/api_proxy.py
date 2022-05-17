import logging
import requests

from rest_framework.exceptions import ValidationError

from requests.auth import HTTPBasicAuth

from .core import BaseApiProxy

logger = logging.getLogger()


class Fs2ApiProxy(BaseApiProxy):
    """ Унаследованный класс для взаимодействия с апи фс2. """

    def __init__(self, login, password='', auth_type=HTTPBasicAuth, need_init=True):
        self.login = login
        self.password = password

        self.session = requests.Session()
        self.session.auth = auth_type(self.login, self.password)

        if need_init:
            self._init_fs2_api()

    def _get_db_uris(self, db_open_response):
        """
        Внутренняя функция для наполения uri's необходимых для работы БД.
        """
        try:  # serializer
            self.inbox_uri = db_open_response['inboxuri']
            self.outbox_uri = db_open_response['outboxuri']
            self.my_staff_uri = db_open_response['mystaffuri']
            self.errands_uri = db_open_response['errandsuri']
            self.new_ent_dlg_uri = db_open_response['newentdlguri']
            self.workspace_uri = db_open_response['workspaceuri']
        except KeyError as key_err:
            error_message = {
                'detail': 'Не удалось извлечь необходимый для работы uri',
                'source': str(key_err),
                'status': 400,
            }
            logger.error(error_message)
            raise ValidationError(error_message)
        except Exception as exc:
            error_message = {
                'detail': 'Вознила непредвиденная ошибка',
                'source': str(exc),
                'status': 400,
            }
            logger.error(error_message)
            raise ValidationError(error_message)

    def init_with_db_datas(self, login, password, app_id, db_id, auth_type=HTTPBasicAuth):
        """ Инициализировать объект апи. """
        self.login = login
        self.password = password
        self.session.auth = auth_type(self.login, self.password)
        self.app_id = app_id
        self.db_id = db_id
        self.db_open_uri = f'/dbopen?appid={app_id}&dbid={db_id}'

        if not self.is_alive():  # NOTE
            self._init_fs2_api()
        else:
            db_open_response, status_code = self.json_request('get', self.API_URL + self.db_open_uri)
            self._get_db_uris(db_open_response)

    def _init_fs2_api(self):
        """
        Открыть соединение с фс2 апи, проинициализировать БД, сохранить основные uris.
        """
        appstart_url = f'{self.API_URL}{self.APP_START_URI}'
        app_start_response, status_code = self.json_request('get', appstart_url)
        self.app_id = app_start_response['id']

        for i in app_start_response.get('databases', {}).get('items', []):
            if i.get('name') == self.DB_NAME:
                self.db_id = i['id']
                self.db_open_uri = i['dbopenuri']

        if not self.db_id or not self.db_open_uri:
            raise ValidationError({
                'detail': f'Не удалось найти информацию по базе данных {self.DB_NAME}',
                'source': '',
                'status': 400,
            })

        db_open_response, status_code = self.json_request('get', self.API_URL + self.db_open_uri)
        self._get_db_uris(db_open_response)

    def documents(self):
        """ По имеющимся inbox_url и outbox_url вернуть лист Records (docs). """
        inbox_docs, status_code = self.json_request('get', self.API_URL + self.inbox_uri)
        # outbox_docs, status_code = self.json_request('get', self.API_URL + self.outbox_uri)
        return inbox_docs.get('records', [])  # + outbox_docs.get('records', [])

    def tasks(self):
        """ По имеющимся my_staff_uri и errands_uri вернуть лист Records (tasks). """
        my_staff, status_code = self.json_request('get', self.API_URL + self.my_staff_uri)
        errands, status_code = self.json_request('get', self.API_URL + self.errands_uri)
        return my_staff.get('records', []) + errands.get('records', [])

    def init_support_request(self):
        """ Инициализация запроса в саппорт (заявка в ЦОД). """
        half_url = f'/SupportRequest?appid={self.app_id}'
        json_resp = self.json_request('get', self.API_URL + half_url)
        return json_resp

    def send_support_request(self, data):
        """ Непосредственно шлем запрос в ЦОД, данные уже валидированы. """
        half_url = f'/SupportRequest?appid={self.app_id}'
        headers = {'Content-type': 'application/json'}
        response = self.request('post', self.API_URL + half_url, headers=headers, json=data)
        return response

    def add_attach_support_request(self, valid_data: dict, file_dest: str) -> dict:
        """ Добавить вложение к запросу в ЦОД (binary в пост запросе). """
        file = open(file_dest, 'rb')
        filename = file_dest.split('/')[-1]
        half_url = f'/actaddattach?appid={valid_data["app_id"]}&eid={valid_data["entityid"]}&fn={filename}'
        response = self.request('post', self.API_URL + half_url, data=file)
        return response
