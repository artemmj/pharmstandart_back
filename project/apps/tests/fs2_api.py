import os
import json
import logging

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from api.v1.documents.serializers import ListAllDocumentsSerializer

logger = logging.getLogger('django')


class Fs2PortalApisTests(APITestCase):
    def setUp(self):
        self.email = 'aamakarenko@pharmstd.ru'
        self.password = 'dS168xV1^^^'

        resp = self.client.post(
            reverse('api_v1:api-root:user-login'),
            data={
                'email': self.email,
                'password': self.password,
            })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.token = json.loads(resp.content.decode('utf-8'))['token']

    def test_get_documents(self):
        """ Получение документов. """
        resp = self.client.get(
            reverse('api_v1:api-root:documents-list'),
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        jresp = json.loads(resp.content.decode('utf-8'))
        serializer = ListAllDocumentsSerializer(data=jresp['results'], many=True)
        serializer.is_valid(raise_exception=True)

    def test_get_tasks(self):
        """ Получение задач. """
        resp = self.client.get(
            reverse('api_v1:api-root:tasks-list'),
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_support_request(self):
        """ Создание запроса в саппорт. """
        resp = self.client.get(
            reverse('api_v1:api-root:datacenter-init-support-request'),
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        init_json_resp = json.loads(resp.content.decode('utf-8'))

        # Добавить вложение
        fl = open('test.txt', 'wb')
        fl.write(b'test')
        fl.close()
        fl = open('test.txt', 'rb')
        add_attach_resp = self.client.post(
            reverse('api_v1:api-root:datacenter-add-attach-support-req'),
            data={
                'entityid': init_json_resp['entityid'],
                'app_id': init_json_resp['app_id'],
                'file': fl,
            },
            HTTP_AUTHORIZATION=f'JWT {self.token}',
            CONTENT_TYPE='multipart/form-data',
        )
        self.assertEqual(add_attach_resp.status_code, status.HTTP_200_OK)
        fl.close()
        os.remove('test.txt')

        send_resp = self.client.post(
            reverse('api_v1:api-root:datacenter-send-support-request'),
            data={
                'entityid': init_json_resp['entityid'],
                'supporttypeid': init_json_resp['directions'][0]['id'],
                'priority': 1,
                'subject': 'test test test',
                'text': 'test test test',
                'app_id': init_json_resp['app_id'],
            },
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(send_resp.status_code, status.HTTP_200_OK)

    def _get_document(self) -> dict:
        """ Ф-ция, получает документ и возвращает его в dict."""

        resp = self.client.get(
            reverse('api_v1:api-root:documents-list'),
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        jresp = json.loads(resp.content.decode('utf-8'))
        if len(jresp['results']) < 1:
            logger.info(f'Нет документов у учетки {self.email}!')
            return
        doc_id = jresp['results'][0]['id']

        resp = self.client.get(
            reverse('api_v1:api-root:documents-detail', args=[doc_id]),
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(type(json.loads(resp.content.decode('utf-8'))), dict)
        jresp = json.loads(resp.content.decode('utf-8'))
        # serializer = DetailedDocumentSerializer(data=jresp)
        # serializer.is_valid(raise_exception=True)
        return jresp

    def test_make_action_add_comment_with_doc(self):
        doc_data = self._get_document()
        action_id = None

        for action in doc_data['actions']:
            if action['action_type'] == 'atComment':
                action_id = action['id']

        if not action_id:
            logger.info(f'В документе {doc_data["name"]} не найдено действие \'Добавить комментарий\'.')
            return

        # Prepare action.
        prepare_resp = self.client.post(
            reverse('api_v1:api-root:documents-prepare-action'),
            data={'action_id': action_id},
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(prepare_resp.status_code, status.HTTP_200_OK)
        jresp = json.loads(prepare_resp.content.decode('utf-8'))
        prep_id = jresp['id']

        # Добавить вложение
        fl = open('test.txt', 'wb')
        fl.write(b'test')
        fl.close()
        fl = open('test.txt', 'rb')
        add_attach_resp = self.client.post(
            reverse('api_v1:api-root:documents-send-attach'),
            data={'action_id': prep_id, 'file': fl},
            HTTP_AUTHORIZATION=f'JWT {self.token}',
            CONTENT_TYPE='multipart/form-data',
        )
        self.assertEqual(add_attach_resp.status_code, status.HTTP_200_OK)
        os.remove('test.txt')

        # Commit action
        data = {
            "action_id": prep_id,
            "comment": "test test test test test test"
        }
        commit_resp = self.client.post(
            reverse('api_v1:api-root:documents-commit-action'),
            data=data,
            HTTP_AUTHORIZATION=f'JWT {self.token}',
        )
        self.assertEqual(commit_resp.status_code, status.HTTP_200_OK)
