import uuid

from django.db import transaction

from apps import app
from apps.fs2_api.api_proxy import Fs2ApiProxy
from apps.user.models import PharmUser


@app.task
@transaction.atomic
def update_pharm_users():
    fs2 = Fs2ApiProxy(login='aamakarenko@pharmstd.ru', password='dS168xV1^^^')

    recver = 1
    suspcnt = 20

    while True:
        uri = f'https://api.pharmstd.ru/users?appid={fs2.app_id}&recver={recver}&suspcnt={suspcnt}'

        resp, status_code = fs2.json_request('get', uri)
        records = resp.get('records', [])
        if len(records) == 0:
            break
        for idx, record in enumerate(records):
            phuser_uuid = uuid.UUID(str(record['id']))
            phuser, created = PharmUser.objects.get_or_create(
                pharm_id=phuser_uuid,
                defaults={
                    'username': record['username'],
                    'email': record['email'],
                    'fio': record['fio'],
                    'userstate': record['userstate'],
                    'phone1': record['phone1'],
                    'phone2': record['phone2'],
                    'firm': record['firm'],
                    'depart': record['depart'],
                    'empl': record['empl'],
                    'abs_reason': record['absreason'],
                }
            )
            if idx == len(records) - 1:
                recver = record['recordversion']
