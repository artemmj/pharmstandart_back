import requests
import logging

from datetime import datetime

from django.http.response import HttpResponse

from requests_ntlm import HttpNtlmAuth
from dateutil.relativedelta import relativedelta

from .core import BaseApiProxy

logger = logging.getLogger('django')


class PortalApiProxy(BaseApiProxy):
    """ Унаследованный класс для взаимодействия с апи портала. """
    PORTAL_URL = 'https://portal.pharmstd.ru'

    def __init__(self, login, password='', auth_type=HttpNtlmAuth):
        self.login = login
        self.password = password

        self.session = requests.Session()
        self.session.auth = auth_type(self.login, self.password)

    def get_tasks_count(self):
        return self.json_request('get', f'{self.PORTAL_URL}/_vti_bin/MobileStd/FarmSed.svc/Count')[0]

    def get_mails_count(self):
        return self.json_request('get', f'{self.PORTAL_URL}/_vti_bin/MobileStd/Mail.svc/Count')[0]

    def get_available_dates_for_pay_sheet(self):
        response, _ = self.json_request('get', f'{self.PORTAL_URL}/_vti_bin/MobileStd/PaySheet.svc/AvailableDate')

        max_date = datetime.strptime(response['Max'], '%Y-%m-%dT%H:%M:%S')
        min_date = datetime.strptime(response['Min'], '%Y-%m-%dT%H:%M:%S')
        # Разбить на по месяцам
        result = []
        while min_date <= max_date:
            result.append({'month': min_date.strftime('%Y-%m-%d')})
            min_date = min_date + relativedelta(months=1)
        return result

    def send_pay_sheet_by_month(self, month):
        date = datetime.strptime(month, '%Y-%m-%d')
        _y, _m, _d = date.year, date.month, date.day
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/PaySheet.svc/Send?dt={_m}/{_d}/{_y}'
        self.json_request('get', url)
        return True

    def get_available_vacation_days_count(self):
        return self.json_request('get', f'{self.PORTAL_URL}/_vti_bin/MobileStd/Vacation.svc/AvailableDays')[0]

    def get_vacation_schedule(self):
        return self.json_request('get', f'{self.PORTAL_URL}/_vti_bin/MobileStd/Vacation.svc/Schedule')[0]

    def get_requests_for_documents(self):
        return self.json_request('get', f'{self.PORTAL_URL}/_vti_bin/MobileStd/RequestOrg.svc/Documents')[0]

    def get_request_org_types(self):
        return self.json_request('get', f'{self.PORTAL_URL}/_vti_bin/MobileStd/RequestOrg.svc/Types')[0]

    def send_request_for_document(self, type_doc, comment, base64files=None):
        data = {'TypeDocument': type_doc, 'Comment': comment}

        if base64files:
            data['Files'] = [{
                'Name': _file['name'],
                'Source': _file['source'].decode('utf-8')
            } for _file in base64files]

        response, status_code = self.json_request(
            'post',
            f'{self.PORTAL_URL}/_vti_bin/MobileStd/RequestOrg.svc/Document',
            json=data
        )
        return response

    def get_employees_from_empcatalog(self) -> dict:
        """ Получить список пользователей для справочника сотрудников. """
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/EmployeesList.svc/Users'
        return self.json_request('get', url)[0]

    def get_structure_from_empcatalog(self) -> dict:
        """ Получить структуру департаментов для справочника сотрудников. """
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/EmployeesList.svc/Structure'
        return self.json_request('get', url)[0]

    def get_elib_statuses(self) -> dict:
        """ Получить статусы elib. """
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/ELibrary.svc/Statuses'
        return self.json_request('get', url)[0]

    def get_elib_rubrics(self) -> dict:
        """ Получить рубрики elib. """
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/ELibrary.svc/Rubrics'
        return self.json_request('get', url)[0]

    def get_elib_categories(self) -> dict:
        """ Получить категории elib. """
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/ELibrary.svc/Categories'
        return self.json_request('get', url)[0]

    def search_elib(self, post_data: dict) -> HttpResponse:
        """
        Шлет запрос на поиск в elib. Данные в post_data
        должны прийти уже валидированными.
        """
        # import requests
        # req = requests.Request('POST', f'{self.PORTAL_URL}/_vti_bin/MobileStd/ELibrary.svc/Search', json=post_data)
        # req = req.prepare()
        # logger.info('{}\n{}\r\n{}\r\n\r\n{}'.format(
        #     '-----------START-----------',
        #     req.method + ' ' + req.url,
        #     '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        #     req.body,
        # ))

        response, _ = self.json_request(
            'post',
            f'{self.PORTAL_URL}/_vti_bin/MobileStd/ELibrary.svc/Search',
            json=post_data,
        )
        return response

    def get_news_birthdays(self) -> dict:
        """ Функция возвращает информацию о днях рождениях.
        """
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/Birthday.svc/Data'
        return self.json_request('get', url)[0]

    def get_news_personnel_changes(self) -> dict:
        """ Функция возвращает информацию о персональных предложениях.
        """
        url = f'{self.PORTAL_URL}/_vti_bin/MobileStd/StaffNews.svc/Data'
        return self.json_request('get', url)[0]
