import uuid
import base64
import logging

from uuid import uuid4
from base64 import b64encode
from datetime import datetime, timedelta

from django.core.cache import cache
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as djangoValidationError

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from saml import schema
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from apps.fs2_api.portal_proxy import PortalApiProxy
from apps.fs2_api.api_proxy import Fs2ApiProxy


User = get_user_model()
logger = logging.getLogger()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def auth_via_pharm_apis(request):
    """
    Перед авторизаций пользователя в мобильном приложении необходимо проверить,
    что введенные им криды (логин и пароль) коректны для апи портала. Для этого
    на первом этапе выполяется запрос в апи портала с переданными кридами.
    Если ответ корректен, считаем, что криды правильные, и либо создаем нового
    пользователя если его нет, либо обновляем его данные при необходимости.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    # Проверка для тестового пользователя TODO исправить этот ужас
    try:
        user = User.objects.get(email=email)
        if user.is_test_user:
            credentials = {'email': email, 'password': password}
            if all(credentials.values()):
                user = authenticate(**credentials)
                if user:
                    if not user.is_active:
                        msg = 'User account is disabled.'
                        raise serializers.ValidationError(msg)
                else:
                    user, _ = User.objects.get_or_create(email=email, username=email.split('@')[0])

                b64pass = b64encode(password.encode('UTF-8')).decode('UTF-8')
                user.set_password(password)
                user.encryptedpass = b64pass
                user.save()
                payload = jwt_payload_handler(user)
                return {
                    'token': jwt_encode_handler(payload),
                    'is_test_user': user.is_test_user,
                    'username': user.username,
                }
        else:
            raise Exception
    except Exception:
        try:
            validate_email(email)
        except djangoValidationError as exc:
            error_message = {
                'detail': f'Введен некорректный адрес электронной почты: {email}',
                'source': email,
                'status': 401,
                'original_exception': exc,
            }
            logger.error(error_message)
            raise ValidationError(error_message)

        if email.split('@')[-1] != 'pharmstd.ru':
            error_message = {
                'detail': 'Некорректный домен электронной почты (требуется @pharmstd.ru)',
                'source': email,
                'status': 401,
            }
            logger.error(error_message)
            raise ValidationError(error_message)

        # Проверка на аутентификацию в апи портала
        try:
            portal_proxy = PortalApiProxy(email.split('@')[0], password)
            portal_proxy.get_mails_count()
        except Exception as original_exc:
            error_message = {
                'detail': 'Не удается авторизоваться в апи портала',
                'source': email,
                'status': 400,
                'original_exception': original_exc,
            }
            logger.error(error_message)
            raise ValidationError(error_message)

        # Проверка на аутентификацию в апи фс2
        try:
            Fs2ApiProxy(email.split('@')[0], password)
        except Exception as original_exc:
            error_message = {
                'detail': 'Не удается авторизоваться в апи фс2',
                'source': email,
                'status': 400,
                'original_exception': original_exc,
            }
            logger.error(error_message)
            raise ValidationError(error_message)

        # Проверка в апи портала прошла успешно, криды корректные

        credentials = {'email': email, 'password': password}
        if all(credentials.values()):
            user = authenticate(**credentials)
            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)
            else:
                user, _ = User.objects.get_or_create(
                    email=email,
                    username=email.split('@')[0],
                )

            b64pass = b64encode(password.encode('UTF-8')).decode('UTF-8')
            user.set_password(password)
            user.encryptedpass = b64pass
            user.save()
            payload = jwt_payload_handler(user)
            return {
                'token': jwt_encode_handler(payload),
                'is_test_user': user.is_test_user,
                'username': user.username,
            }


def get_vacation_count_actual_days(user):
    ''' Получить количество доступных дней для отпуска '''
    api = PortalApiProxy(user.email.split('@')[0], user.get_enc_pass)
    return api.get_available_vacation_days_count()


def get_vacation_schedule(user):
    ''' Получить расписание отпуска '''
    api = PortalApiProxy(user.email.split('@')[0], user.get_enc_pass)
    api_schedule = api.get_vacation_schedule()
    fact_datas = api_schedule.get('Fact', {})
    plan_datas = api_schedule.get('Plan', {})

    last_update = None
    if plan_datas:
        last_update = datetime.fromtimestamp(int(plan_datas['LastUpdate'][6:16])) + timedelta(hours=3)

    result_data = {
        's_error': api_schedule.get('s_error', bool),
        's_message': api_schedule.get('s_message', str),
        'fact': {
            'available_days': fact_datas['AvailableDays'] if fact_datas else None,
            'total': fact_datas['Total'] if fact_datas else None,
            'rows': [],
        },
        'plan': {
            'last_update': last_update,
            'total': plan_datas['Total'] if plan_datas else None,
            'rows': [],
        },
    }

    if fact_datas and plan_datas:
        fact_rows = fact_datas.get('Rows', [])
        plan_rows = plan_datas.get('Rows', [])

        for row in fact_rows:
            result_data['fact']['rows'].append({
                'count': row['Count'],
                'start': datetime.fromtimestamp(int(row['Start'][6:16])) + timedelta(hours=3),
                'end': datetime.fromtimestamp(int(row['End'][6:16])) + timedelta(hours=3),
            })

        for row in plan_rows:
            result_data['plan']['rows'].append({
                'count': row['Count'],
                'start': datetime.fromtimestamp(int(row['Start'][6:16])) + timedelta(hours=3),
                'end': datetime.fromtimestamp(int(row['End'][6:16]))
            })

    return result_data


def get_requests_for_documents(user):
    ''' Получить все заявки пользователя на документы. '''
    api = PortalApiProxy(user.email.split('@')[0], user.get_enc_pass)
    api_result = api.get_requests_for_documents()

    if api_result['Count'] < 1:
        return []

    return_data = []
    rows = api_result.get('Rows', [])
    for row in rows:
        return_data.append({
            'title': row['Title'],
            'created_date': datetime.fromtimestamp(int(row['CreateDate'][6:16])) + timedelta(hours=3),
            'modified_date': datetime.fromtimestamp(int(row['ModifiedDate'][6:16])) + timedelta(hours=3),
            'type': row['Type'],
            'status': row['Status'],
            'department': row['Department'],
            'author_comment': row['AuthorComment'],
            'looked': row['Looked'],
            'author_name': row['AuthorName'],
            'author_login': row['AuthorLogin'],
            'editor_name': row['EditorName'],
            'editor_login': row['EditorLogin'],
            'attachments_count': row['AttachmentsCount'],
        })

    return return_data


def get_request_org_types(user):
    ''' Получить возможные типы документов для заявки. '''
    api = PortalApiProxy(user.email.split('@')[0], user.get_enc_pass)
    api_result = api.get_request_org_types()

    return_data = []
    types = api_result.get('Result', [])
    for _type in types:
        # Типы нужно положить в кэш, чтобы
        # в дальнейшем отправлять запрос NOTE
        type_id = uuid.uuid4()
        obj = {'id': type_id, 'name': _type['Name'], 'order': _type['Order']}
        cache.set(type_id, obj)
        return_data.append(obj)

    return return_data


def send_request_document(request, serializer_data):
    ''' Послать запрос на заявку на получение документа. '''
    files_data = list()

    if 'files' in serializer_data:
        for _file in serializer_data['files']:
            with open(_file, 'rb') as ofile:
                encouded_file = base64.b64encode(ofile.read())
            files_data.append({'name': _file.split('/')[-1], 'source': encouded_file})

    api = PortalApiProxy(request.user.email.split('@')[0], request.user.get_enc_pass)
    request_data = {
        'type_doc': serializer_data['type_document'],
        'comment': serializer_data['comment'],
    }
    if files_data:
        request_data['base64files'] = files_data

    result = api.send_request_for_document(**request_data)
    return result


def get_dates_for_pay_sheets(user):
    api = PortalApiProxy(user.email.split('@')[0], user.get_enc_pass)
    return api.get_available_dates_for_pay_sheet()


def send_pay_sheet(user, month):
    api = PortalApiProxy(user.email.split('@')[0], user.get_enc_pass)
    return True if api.send_pay_sheet_by_month(month) else False


def generate_sso_saml_uflex(request):
    document = schema.Response()
    document.id = uuid4()
    document.issue_instant = datetime.now()
    document.issuer = 'msk.phs'
    document.destination = 'https://newcbt.unifest.ru/ExternalAuth/PortalAuth'
    document.status.code.value = schema.StatusCode.SUCCESS

    # Create an assertion for the response.
    document.assertions = assertion = schema.Assertion()
    assertion.id = uuid4()
    assertion.issue_instant = datetime.now()
    assertion.issuer = 'msk.phs'

    # Create a subject.
    assertion.subject = schema.Subject()
    assertion.subject.principal = request.user.email
    assertion.subject.principal.name_qualifier = 'newcbt.unifest.ru'
    data = schema.SubjectConfirmationData()
    data.not_on_or_after = datetime.now()  # ?
    data.recipient = 'https://newcbt.unifest.ru/ExternalAuth/PortalAuth'
    confirmation = schema.SubjectConfirmation()
    confirmation.data = data
    assertion.subject.confirmation = confirmation

    # Create an authentication statement.
    statement = schema.AuthenticationStatement()
    assertion.statements.append(statement)
    statement.authn_instant = datetime(2022, 1, 1, 1, 9)
    schema.AuthenticationContextReference
    statement.context.reference = 'AuthnContextClassRef'

    # Create a authentication condition.
    assertion.conditions = conditions = schema.Conditions()
    conditions.not_before = datetime(2000, 1, 1, 1, 3)
    conditions.not_on_or_after = datetime(2022, 1, 1, 1, 9)
    condition = schema.AudienceRestriction()
    condition.audiences = 'newcbt.unifest.ru'
    conditions.condition = condition

    statement = schema.AttributeStatement()
    assertion.statements.append(statement)
    attribute = schema.Attribute()
    statement.attributes.append(attribute)
    attribute.name_ = 'pass id_Group'
    attribute.name_format = 'urn:oasis:names:tc:SAML:2.0:attrname-format:basic'
    value = schema.AttributeValue()
    value.text = '6184'
    attribute.value = value

    document.tostring()
    # xml_document = document.serialize()

    cert = open("/ssl_key/pharm_ssl.pem").read()
    key = open("/ssl_key/private/pharm_key.pem").read()

    b64data = b64encode(OneLogin_Saml2_Utils.add_sign(document.tostring(), key, cert))
    return b64data
